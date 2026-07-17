from __future__ import annotations

import re
from pathlib import PurePosixPath
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from typing import Any

from ..models import AttackVector, RequestSpec


DEFAULT_DETECTION_EXCLUDE_PATTERNS = [
    r"(^|/)(header|footer|nav|navbar|menu|sidebar|top|bottom|form|forms|layout|template|templates|function|functions|config|database|db|common|constants|settings)\.php$",
    r"(^|/)(includes?|inc|lib|libs?|vendor|templates?|layouts?)/",
    r"(^|/)admin/(modules|styles)/",
]

STATIC_STANDALONE_ENTRY_PATTERN = re.compile(r"(^|/)(install|setup|upgrade)(?:\.php|/|$)", re.I)


def _requests(entry: dict[str, Any], kind: str | None = None) -> list[dict[str, Any]]:
    values = list(entry.get("requests", []))
    return [item for item in values if item.get("kind") == kind] if kind else values


def _request(entry: dict[str, Any], preferred_kind: str | None = None) -> RequestSpec:
    choices = _requests(entry, preferred_kind) or _requests(entry)
    if not choices:
        return RequestSpec()
    selected = choices[0]
    return RequestSpec(
        method=str(selected.get("method", "GET")).upper(),
        params=dict(selected.get("params", {})),
        referer=selected.get("referer"),
    )


def _roles(entry: dict[str, Any], kind: str) -> list[str]:
    return list(
        dict.fromkeys(
            request["role"]
            for request in entry.get("requests", [])
            if request.get("kind") == kind and request.get("role")
        )
    )


def _excluded_detection_page(page: str, patterns: list[str]) -> bool:
    full = str(page).lstrip("/").replace("\\", "/").casefold()
    normalized = PurePosixPath(str(page).split("?", 1)[0].lstrip("/")).as_posix().casefold()
    candidates = [full, normalized]
    return any(re.search(pattern, candidate, re.I) for pattern in patterns for candidate in candidates)


def _static_degrees(graph: dict[str, Any]) -> dict[str, tuple[int, int]]:
    degrees: dict[str, list[int]] = {}
    for edge in graph.get("static_edges", []):
        left = str(edge.get("from", ""))
        right = str(edge.get("to", ""))
        if left:
            degrees.setdefault(left, [0, 0])[1] += 1
        if right:
            degrees.setdefault(right, [0, 0])[0] += 1
    return {key: (value[0], value[1]) for key, value in degrees.items()}


def _static_only_detection_candidate(page: str, graph: dict[str, Any], degrees: dict[str, tuple[int, int]]) -> bool:
    normalized = PurePosixPath(page.split("?", 1)[0].lstrip("/")).as_posix()
    if STATIC_STANDALONE_ENTRY_PATTERN.search(normalized):
        return True
    source = str(graph.get("source_map", {}).get(page, normalized))
    in_degree, out_degree = degrees.get(source, (0, 0))
    return in_degree == 0 and out_degree == 0


def _override_options(keys: list[str], overrides: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not overrides:
        return []
    options: list[dict[str, Any]] = [{}]
    used = False
    for key in keys:
        if key not in overrides:
            continue
        used = True
        raw_value = overrides[key]
        values = raw_value if isinstance(raw_value, list) else [raw_value]
        options = [{**base, key: value} for base in options for value in values]
    return options if used else []


def _request_with_overrides(entry: dict[str, Any], preferred_kind: str | None, overrides: dict[str, Any]) -> RequestSpec:
    request = _request(entry, preferred_kind)
    return RequestSpec(request.method, {**request.params, **overrides}, request.referer)


def _query_identity_parameters(page: str, identity: set[str]) -> list[str]:
    parsed = urlsplit(page)
    return sorted({key for key, _ in parse_qsl(parsed.query, keep_blank_values=True) if key in identity})


def _page_with_query_overrides(page: str, overrides: dict[str, Any]) -> str:
    if not overrides:
        return page
    parsed = urlsplit(page)
    if not parsed.query:
        return page
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    changed = False
    for key, value in overrides.items():
        if key in query:
            query[str(key)] = str(value)
            changed = True
    if not changed:
        return page
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query, doseq=True), parsed.fragment))

def _canonical_vulnerability_page(page: str) -> str:
    parsed = urlsplit(page)
    normalized_path = PurePosixPath(parsed.path.lstrip("/")).as_posix()
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    if not pairs:
        return normalized_path
    canonical_pairs = [(key, "*") for key in sorted({key for key, _ in pairs})]
    return urlunsplit(("", "", normalized_path, urlencode(canonical_pairs, doseq=True), ""))


def _dedupe_vectors(vectors: list[AttackVector]) -> list[AttackVector]:
    result: list[AttackVector] = []
    seen: set[tuple[Any, ...]] = set()
    for vector in vectors:
        key = (
            vector.category,
            _canonical_vulnerability_page(vector.page),
            vector.request.method.upper(),
            tuple(sorted((str(key), str(value)) for key, value in vector.request.params.items())),
            tuple(vector.authorized_roles),
            tuple(vector.identity_parameters),
            tuple(vector.page_overrides),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(vector)
    return result


def _configured_horizontal_page_overrides(page: str, rules: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if not rules:
        return []
    candidates = [page, PurePosixPath(page.split("?", 1)[0].lstrip("/")).as_posix()]
    matched: list[dict[str, Any]] = []
    for raw in rules:
        if not isinstance(raw, dict):
            continue
        pattern = str(raw.get("pattern") or "")
        exact = str(raw.get("page") or "").lstrip("/")
        if exact and exact not in candidates:
            continue
        if pattern and not any(re.search(pattern, candidate, re.I) for candidate in candidates):
            continue
        pages = raw.get("pages") or raw.get("page_overrides") or raw.get("targets") or []
        if isinstance(pages, str):
            pages = [pages]
        pages = [str(item).lstrip("/") for item in pages if str(item).strip()]
        if not pages:
            continue
        request_variants = raw.get("request_variants") or [{}]
        if isinstance(request_variants, dict):
            request_variants = [request_variants]
        matched.append({
            "pages": pages,
            "identity_parameters": [str(item) for item in raw.get("identity_parameters", ["path"])],
            "request_variants": [dict(item) for item in request_variants if isinstance(item, dict)] or [{}],
        })
    return matched


def _request_with_variant(entry: dict[str, Any], preferred_kind: str | None, variant: dict[str, Any]) -> RequestSpec:
    request = _request(entry, preferred_kind)
    params = {**request.params, **dict(variant.get("params", {}))}
    method = str(variant.get("method") or request.method).upper()
    referer = variant.get("referer", request.referer)
    return RequestSpec(method, params, referer)

def generate_vectors(
    graph: dict[str, Any],
    identity_parameters: list[str],
    static_exclude_patterns: list[str] | None = None,
    force_static_pages: list[str] | None = None,
    force_horizontal_pages: list[str] | None = None,
    horizontal_exclude_patterns: list[str] | None = None,
    vertical_only_patterns: list[str] | None = None,
    force_vertical_pages: list[str] | None = None,
    vertical_overrides: dict[str, Any] | None = None,
    post_page_open_get_patterns: list[str] | None = None,
    horizontal_page_overrides: list[dict[str, Any]] | None = None,
    admin_only_exclude_patterns: list[str] | None = None,
    authenticated_only_exclude_patterns: list[str] | None = None,
) -> list[AttackVector]:
    vectors: list[AttackVector] = []
    identity = set(identity_parameters)
    detection_patterns = [*DEFAULT_DETECTION_EXCLUDE_PATTERNS, *(static_exclude_patterns or [])]
    horizontal_exclude = [re.compile(str(pattern), re.I) for pattern in (horizontal_exclude_patterns or [])]
    admin_only_exclude = [re.compile(str(pattern), re.I) for pattern in (admin_only_exclude_patterns or [])]
    authenticated_only_exclude = [re.compile(str(pattern), re.I) for pattern in (authenticated_only_exclude_patterns or [])]
    vertical_only = [re.compile(str(pattern), re.I) for pattern in (vertical_only_patterns or [])]
    post_page_open_get = [re.compile(str(pattern), re.I) for pattern in (post_page_open_get_patterns or [])]
    forced_static_pages_raw = [str(page).lstrip("/") for page in (force_static_pages or [])]
    forced_static = {PurePosixPath(page).as_posix() for page in forced_static_pages_raw}
    forced_horizontal = {
        PurePosixPath(str(page).split("?", 1)[0].lstrip("/")).as_posix()
        for page in (force_horizontal_pages or [])
    }
    forced_horizontal.update(
        PurePosixPath(str(page).lstrip("/")).as_posix() for page in (force_horizontal_pages or [])
    )
    forced_vertical = {
        PurePosixPath(str(page).split("?", 1)[0].lstrip("/")).as_posix()
        for page in (force_vertical_pages or [])
    }
    forced_vertical.update(
        PurePosixPath(str(page).lstrip("/")).as_posix() for page in (force_vertical_pages or [])
    )
    degrees = _static_degrees(graph)
    static_detection_pages = list(graph.get("static_detection_pages", graph.get("static_only", [])))
    has_explicit_static_detection_set = "static_detection_pages" in graph

    for page in static_detection_pages:
        normalized = PurePosixPath(page.split("?", 1)[0].lstrip("/")).as_posix()
        forced = page in forced_static or normalized in forced_static
        if not forced and _excluded_detection_page(page, detection_patterns):
            continue
        if not has_explicit_static_detection_set and not forced and not _static_only_detection_candidate(page, graph, degrees):
            continue
        request = _request(graph.get("access", {}).get(page, {})) if page in graph.get("access", {}) else RequestSpec()
        vectors.append(AttackVector("static_only", page, [], request))

    for page, entry in graph.get("access", {}).items():
        normalized_page = PurePosixPath(page.split("?", 1)[0].lstrip("/")).as_posix()
        if _excluded_detection_page(page, detection_patterns):
            continue
        kinds = set(entry.get("kinds", []))
        vertical_only_page = any(pattern.search(page) for pattern in vertical_only)
        admin_only_excluded = any(pattern.search(page) for pattern in admin_only_exclude)
        authenticated_only_excluded = any(pattern.search(page) for pattern in authenticated_only_exclude)
        if not vertical_only_page and not admin_only_excluded and kinds == {"admin"}:
            request = _request(entry, "admin")
            vectors.append(
                AttackVector(
                    "admin_only",
                    page,
                    _roles(entry, "admin") or list(entry.get("roles", [])),
                    request,
                )
            )
            if request.method.upper() == "POST" and any(pattern.search(page) for pattern in post_page_open_get):
                vectors.append(
                    AttackVector(
                        "admin_only",
                        page,
                        _roles(entry, "admin") or list(entry.get("roles", [])),
                        RequestSpec(method="GET", params={}, referer=request.referer),
                    )
                )
        elif not vertical_only_page and not authenticated_only_excluded and "visitor" not in kinds and kinds & {"user", "admin"}:
            request = _request(entry, "user")
            vectors.append(
                AttackVector(
                    "authenticated_only",
                    page,
                    _roles(entry, "user") or list(entry.get("roles", [])),
                    request,
                )
            )
            if request.method.upper() == "POST" and any(pattern.search(page) for pattern in post_page_open_get):
                vectors.append(
                    AttackVector(
                        "authenticated_only",
                        page,
                        _roles(entry, "user") or list(entry.get("roles", [])),
                        RequestSpec(method="GET", params={}, referer=request.referer),
                    )
                )

        matched = sorted(
            {
                key
                for request in _requests(entry, "user")
                for key in request.get("params", {})
                if key in identity
            }
            | set(_query_identity_parameters(page, identity))
        )
        forced_horizontal_page = page in forced_horizontal or normalized_page in forced_horizontal
        forced_vertical_page = page in forced_vertical or normalized_page in forced_vertical
        horizontal_excluded = any(pattern.search(page) for pattern in horizontal_exclude)
        page_override_rules = _configured_horizontal_page_overrides(page, horizontal_page_overrides)
        if page_override_rules and not vertical_only_page and not horizontal_excluded:
            for rule in page_override_rules:
                for variant in rule["request_variants"]:
                    vectors.append(
                        AttackVector(
                            "horizontal",
                            page,
                            _roles(entry, "user"),
                            _request_with_variant(entry, "user", variant),
                            rule["identity_parameters"],
                            rule["pages"],
                        )
                    )
        if matched and forced_vertical_page:
            for overrides in _override_options(matched, vertical_overrides):
                vectors.append(
                    AttackVector(
                        "vertical",
                        _page_with_query_overrides(page, overrides),
                        _roles(entry, "admin") or [role for role in entry.get("roles", []) if role],
                        _request_with_overrides(entry, "admin", overrides),
                        matched,
                    )
                )
        if matched and not vertical_only_page and not horizontal_excluded and ("visitor" not in kinds or forced_horizontal_page):
            vectors.append(
                AttackVector(
                    "horizontal",
                    page,
                    _roles(entry, "user"),
                    _request(entry, "user"),
                    matched,
                )
            )
    # Generate static_only GET vectors for force_static_pages that appear in
    # the access graph but were filtered out of static_only because a crawler
    # role visited them.  These pages (e.g. setup.php) may have been crawled
    # with a POST / form-submission request; a separate GET-based static_only
    # check ensures we also test whether the page is reachable without
    # authentication via a plain GET.
    existing_static_pages = {v.page for v in vectors if v.category == "static_only"}
    explicit_detection_pages = {str(page) for page in static_detection_pages}
    for page in graph.get("access", {}):
        normalized = PurePosixPath(page.split("?", 1)[0].lstrip("/")).as_posix()
        if has_explicit_static_detection_set and page not in explicit_detection_pages and normalized not in explicit_detection_pages:
            continue
        if (page not in forced_static and normalized not in forced_static):
            continue
        if page in existing_static_pages:
            continue
        if _excluded_detection_page(page, detection_patterns):
            continue
        request = _request(graph.get("access", {}).get(page, {})) if page in graph.get("access", {}) else RequestSpec()
        vectors.append(AttackVector("static_only", page, [], request))


    return _dedupe_vectors(vectors)







