from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit


def absolute_url(base_url: str, value: str) -> str:
    return urljoin(base_url.rstrip("/") + "/", value)


def in_scope(url: str, base_url: str, scope_path: str | None = None) -> bool:
    candidate = urlsplit(url)
    base = urlsplit(base_url)
    if candidate.scheme not in {"http", "https"} or candidate.netloc != base.netloc:
        return False
    prefix = scope_path if scope_path is not None else base.path
    prefix = prefix or "/"
    return candidate.path.startswith(prefix)


def canonical_page(
    url: str,
    base_url: str,
    preserve_parameters: list[str] | None = None,
    drop_parameters: list[str] | None = None,
    path_parameter_patterns: list[Any] | None = None,
) -> str:
    preserve = set(preserve_parameters or [])
    drop = set(drop_parameters or [])
    parsed = urlsplit(absolute_url(base_url, url))
    base = urlsplit(base_url)
    path = parsed.path
    if base.path != "/" and path.startswith(base.path):
        path = path[len(base.path):]
    path = path.lstrip("/") or "./"
    for raw in path_parameter_patterns or []:
        if isinstance(raw, dict):
            pattern = str(raw.get("pattern", ""))
            replacement = str(raw.get("replacement", raw.get("replace", "")))
        else:
            pattern = str(raw)
            replacement = "p1"
        if pattern and re.search(pattern, path, re.I):
            path = re.sub(pattern, replacement, path, flags=re.I)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key in drop:
            continue
        query.append((key, value if key in preserve else "p1"))
    query.sort()
    return urlunsplit(("", "", path, urlencode(query, doseq=True), ""))


def request_params(url: str, post_data: str | None = None) -> dict[str, str]:
    values = dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
    if post_data:
        values.update(dict(parse_qsl(post_data, keep_blank_values=True)))
    return values


