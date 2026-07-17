from __future__ import annotations

import ast
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from ..config import TargetConfig


SOURCE_EXTENSIONS = {
    "php": {".php"},
    "python": {".py"},
    "go": {".go"},
    "java": {".java", ".jsp"},
    "jsp": {".java", ".jsp"},
}

COMPONENT_PATH_PATTERN = re.compile(
    r"(^|/)(includes?|inc|lib|libs?|vendor|templates?|layouts?|partials?|components?|static|assets|css|js|images?|img|fonts?)/"
    r"|(^|/)(header|footer|nav|navbar|menu|sidebar|top|bottom|form|forms|layout|template|templates|function|functions|config|database|db|common|constants|settings)\.[A-Za-z0-9]+$",
    re.I,
)

STATIC_ASSET_EXTENSIONS = {
    ".css", ".js", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".webp",
    ".pdf", ".zip", ".rar", ".7z", ".tar", ".gz", ".mp3", ".mp4", ".avi",
    ".woff", ".woff2", ".ttf", ".eot",
}

STANDALONE_ENTRY_PATTERN = re.compile(r"(^|/)(install|setup|upgrade)(?:\.[A-Za-z0-9]+|/|$)", re.I)


def _files(root: Path, extensions: set[str], skip_dirs: Iterable[str]) -> list[Path]:
    skipped = {item.casefold() for item in skip_dirs}
    result = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
        relative_parts = {part.casefold() for part in path.relative_to(root).parts[:-1]}
        if relative_parts & skipped:
            continue
        result.append(path.resolve())
    return result


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _is_component_like(relative: str) -> bool:
    return bool(COMPONENT_PATH_PATTERN.search(relative.replace("\\", "/")))


def _strip_query_fragment(value: str) -> str:
    return value.split("#", 1)[0].split("?", 1)[0]


def _normalize_http_target(value: str, current_relative: str) -> str | None:
    target = value.strip()
    if not target or target.startswith("#"):
        return None
    lowered = target.lower()
    if lowered.startswith(("http://", "https://", "mailto:", "tel:", "javascript:", "data:")):
        return None
    target = _strip_query_fragment(target)
    if not target:
        return None
    if any(ch in target for ch in "<>|*\x00"):
        return None
    suffix = Path(target).suffix.lower()
    if suffix in STATIC_ASSET_EXTENSIONS:
        return None
    if target.startswith("/"):
        normalized = target.lstrip("/")
    else:
        normalized = (PurePosixPath(current_relative).parent / target).as_posix()
    normalized = re.sub(r"/+", "/", normalized).lstrip("./")
    return normalized or "./"


def _resolve_file(base: Path, value: str, root: Path, candidates: set[Path]) -> Path | None:
    # Static include/import extraction can see dynamic expressions in legacy PHP.
    # If the extracted value is not a valid filesystem path on Windows, it is not
    # a resolvable static edge and should be ignored.
    try:
        direct = (base / value).resolve()
    except OSError:
        direct = None
    if direct in candidates:
        return direct
    try:
        rooted = (root / value.lstrip("/")).resolve()
    except OSError:
        return None
    return rooted if rooted in candidates else None


def _php_edges(path: Path, root: Path, candidates: set[Path]) -> set[Path]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"(?:include|include_once|require|require_once)\s*(?:\(\s*)?['\"]([^'\"]+)['\"]",
        re.I,
    )
    return {
        target
        for value in pattern.findall(content)
        if (target := _resolve_file(path.parent, value, root, candidates)) is not None
    }


def _python_edges(path: Path, root: Path, candidates: set[Path]) -> set[Path]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()
    targets = set()
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        for module in modules:
            module_path = Path(*module.split("."))
            for candidate in (root / module_path.with_suffix(".py"), root / module_path / "__init__.py"):
                resolved = candidate.resolve()
                if resolved in candidates:
                    targets.add(resolved)
    return targets


def _go_edges(path: Path, root: Path, candidates: set[Path]) -> set[Path]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    imports = re.findall(r'^\s*"([^\"]+)"\s*$', content, re.M)
    result = set()
    for value in imports:
        suffix = Path(*value.split("/"))
        directories = [root / suffix, root / suffix.name]
        for directory in directories:
            for candidate in candidates:
                if candidate.parent == directory.resolve():
                    result.add(candidate)
    return result


def _java_edges(path: Path, root: Path, candidates: set[Path]) -> set[Path]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    result = set()
    if path.suffix.lower() == ".jsp":
        for value in re.findall(r'<%@\s*include\s+file=["\']([^"\']+)["\']', content, re.I):
            target = _resolve_file(path.parent, value, root, candidates)
            if target:
                result.add(target)
    for value in re.findall(r"^\s*import\s+([\w.]+);", content, re.M):
        target_suffix = Path(*value.split(".")).with_suffix(".java")
        matches = [candidate for candidate in candidates if candidate.as_posix().endswith(target_suffix.as_posix())]
        result.update(matches)
    return result


def _python_module_file(root: Path, module_parts: list[str], candidates: set[Path]) -> Path | None:
    if not module_parts:
        return None
    module_path = Path(*module_parts)
    for candidate in (root / module_path.with_suffix(".py"), root / module_path / "__init__.py"):
        resolved = candidate.resolve()
        if resolved in candidates:
            return resolved
    return None


def _python_import_sources(path: Path, root: Path, candidates: set[Path]) -> dict[str, Path]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return {}
    try:
        package_parts = list(path.resolve().relative_to(root.resolve()).with_suffix("").parts[:-1])
    except ValueError:
        package_parts = []
    imports: dict[str, Path] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_parts = alias.name.split(".")
                source = _python_module_file(root, module_parts, candidates)
                if not source and len(module_parts) == 1:
                    local = (path.parent / module_parts[0]).with_suffix(".py").resolve()
                    if local in candidates:
                        source = local
                if source:
                    imports[alias.asname or module_parts[0]] = source
        elif isinstance(node, ast.ImportFrom):
            module_parts = node.module.split(".") if node.module else []
            if node.level:
                base = package_parts[: max(0, len(package_parts) - node.level + 1)]
                module_parts = [*base, *module_parts]
            source = _python_module_file(root, module_parts, candidates)
            for alias in node.names:
                local_name = alias.asname or alias.name
                nested = None if alias.name == "*" else _python_module_file(root, [*module_parts, alias.name], candidates)
                if nested:
                    imports[local_name] = nested
                elif source:
                    imports[local_name] = source
    return imports


def _python_view_source(view: ast.AST, imports: dict[str, Path]) -> Path | None:
    if isinstance(view, ast.Name):
        return imports.get(view.id)
    if isinstance(view, ast.Attribute):
        root = view.value
        while isinstance(root, ast.Attribute):
            root = root.value
        if isinstance(root, ast.Name):
            return imports.get(root.id)
    if isinstance(view, ast.Call):
        return _python_view_source(view.func, imports)
    return None



def _python_django_path_route(value: str) -> str:
    route = value.strip().lstrip("/") or "./"
    route = re.sub(r"<[^>]+>", "p1", route)
    return route or "./"


def _python_django_regex_route(value: str) -> str | None:
    route = value.strip()
    if not route:
        return None
    if not (route.startswith("^") or route.endswith("$") or "/" in route):
        return None
    route = route.lstrip("^").rstrip("$")
    if not route:
        return "./"
    route = re.sub(r"\(\?P<([^>]+)>\\d\+\)", "p1", route)
    route = re.sub(r"\(\?P<([^>]+)>[^)]*\)", "p1", route)
    route = re.sub(r"\(\\d\+\)", "p1", route)
    route = re.sub(r"\([^)]*\)", "p1", route)
    route = route.replace("\\/", "/")
    return route.lstrip("/") or "./"


def _python_route_mappings(path: Path, root: Path, candidates: set[Path], relative: str) -> dict[str, str]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    mappings: dict[str, str] = {}
    for route in re.findall(r"@\w+\.route\(\s*['\"]([^'\"]+)['\"]", content):
        normalized = route.lstrip("/") or "./"
        mappings[normalized] = relative
    try:
        tree = ast.parse(content)
    except SyntaxError:
        for route in re.findall(r"\bpath\(\s*['\"]([^'\"]+)['\"]", content):
            normalized = route.lstrip("/") or "./"
            mappings[normalized] = relative
        return mappings
    imports = _python_import_sources(path, root, candidates)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        func_name = ""
        if isinstance(func, ast.Name):
            func_name = func.id
        elif isinstance(func, ast.Attribute):
            func_name = func.attr
        if func_name not in {"path", "re_path", "url"}:
            continue
        if len(node.args) < 1 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
            continue
        route = node.args[0].value
        normalized = _python_django_regex_route(route) if func_name in {"re_path", "url"} else _python_django_path_route(route)
        if not normalized:
            continue
        source = _python_view_source(node.args[1], imports) if len(node.args) >= 2 else None
        mappings[normalized] = _relative(source, root) if source else relative
    for node in ast.walk(tree):
        if not isinstance(node, ast.Tuple) or len(node.elts) < 2:
            continue
        first = node.elts[0]
        if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
            continue
        normalized = _python_django_regex_route(first.value)
        if not normalized:
            continue
        source = _python_view_source(node.elts[1], imports)
        if source:
            mappings[normalized] = _relative(source, root)
    return mappings


def _go_find_matching_brace(source: str, open_index: int) -> int:
    depth = 0
    in_string: str | None = None
    escaped = False
    i = open_index
    while i < len(source):
        ch = source[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\" and in_string != "`":
                escaped = True
            elif ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in {'"', "'", "`"}:
            in_string = ch
            i += 1
            continue
        if source.startswith("//", i):
            newline = source.find("\n", i)
            i = len(source) if newline == -1 else newline + 1
            continue
        if source.startswith("/*", i):
            end_comment = source.find("*/", i + 2)
            i = len(source) if end_comment == -1 else end_comment + 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return len(source)


def _go_function_sources(root: Path, candidates: set[Path]) -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for candidate in candidates:
        if candidate.suffix.lower() != ".go":
            continue
        content = candidate.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"(?m)^func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\(", content):
            sources.setdefault(match.group(1), candidate)
    return sources


def _go_route_normalize(route: str) -> str:
    route = route.replace("//", "/").strip().lstrip("/")
    route = re.sub(r"\{[^}/]+(?::[^}]+)?\}", "p1", route)
    return route.rstrip("/") or "./"


def _go_chi_route_mappings(path: Path, root: Path, candidates: set[Path], relative: str) -> dict[str, str]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    function_sources = _go_function_sources(root, candidates)
    mappings: dict[str, str] = {}
    stack: list[tuple[int, str]] = []
    route_call = re.compile(
        r"\b(?:[A-Za-z_]\w*)\.(Route|Get|Post|Put|Delete|Patch|Handle|HandleFunc)\(\s*['\"]([^'\"]+)['\"]\s*(?:,\s*([A-Za-z_]\w*))?",
        re.S,
    )

    for match in route_call.finditer(content):
        while stack and match.start() >= stack[-1][0]:
            stack.pop()
        kind, fragment, handler = match.group(1), match.group(2), match.group(3)
        prefix = "/".join(item[1].strip("/") for item in stack if item[1].strip("/"))
        route = _go_route_normalize((prefix + "/" + fragment).strip("/"))
        if kind == "Route":
            open_index = content.find("{", match.end())
            if open_index >= 0:
                stack.append((_go_find_matching_brace(content, open_index), fragment))
            continue
        source = function_sources.get(handler or "") if handler else None
        mappings[route] = _relative(source, root) if source else relative
    return mappings



def _resolve_source_for_url(url: str, root: Path, candidates: set[Path], public_extensions: tuple[str, ...]) -> Path | None:
    clean = _strip_query_fragment(url).lstrip("/")
    if not clean or clean == "./" or any(ch in clean for ch in "<>|*\x00"):
        return None
    try:
        direct = (root / clean).resolve()
    except OSError:
        return None
    if direct in candidates:
        return direct
    if Path(clean).suffix:
        return None
    for ext in public_extensions:
        try:
            candidate = (root / (clean + ext)).resolve()
        except OSError:
            continue
        if candidate in candidates:
            return candidate
    index_candidates = [root / clean / f"index{ext}" for ext in public_extensions]
    for candidate in index_candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in candidates:
            return resolved
    return None


def _http_target_mappings(path: Path, root: Path, candidates: set[Path], relative: str, public_extensions: tuple[str, ...]) -> dict[str, str]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    raw_targets: set[str] = set()
    # Hyperlinks, forms, frames, and other browser-initiated request targets.
    for pattern in [
        r"\b(?:href|action|formaction|src)\s*=\s*['\"]([^'\"]+)['\"]",
        r"\b(?:window\.)?location(?:\.href)?\s*=\s*['\"]([^'\"]+)['\"]",
        r"\b(?:window\.)?location\.replace\(\s*['\"]([^'\"]+)['\"]\s*\)",
        r"\bheader\(\s*['\"]Location\s*:\s*([^'\"]+)['\"]\s*\)",
        r"http-equiv\s*=\s*['\"]refresh['\"][^>]+url\s*=\s*([^'\";>\s]+)",
    ]:
        raw_targets.update(re.findall(pattern, content, re.I | re.S))

    mappings: dict[str, str] = {}
    for raw in raw_targets:
        normalized = _normalize_http_target(raw, relative)
        if not normalized:
            continue
        source = _resolve_source_for_url(normalized, root, candidates, public_extensions)
        if source:
            mappings[normalized] = _relative(source, root)
    return mappings

def _route_mappings(path: Path, language: str, relative: str, root: Path, candidates: set[Path]) -> dict[str, str]:
    content = path.read_text(encoding="utf-8", errors="ignore")
    mappings: dict[str, str] = {}
    if language == "python":
        return _python_route_mappings(path, root, candidates, relative)
    if language == "go":
        chi_mappings = _go_chi_route_mappings(path, root, candidates, relative)
        if chi_mappings:
            return chi_mappings
        patterns = [r"\b(?:HandleFunc|Handle|GET|POST|PUT|DELETE)\(\s*['\"]([^'\"]+)['\"]"]
    elif language in {"java", "jsp"}:
        patterns = [r"@WebServlet\(\s*['\"]([^'\"]+)['\"]"]
    else:
        patterns = []
    for pattern in patterns:
        for route in re.findall(pattern, content):
            normalized = route.lstrip("/") or "./"
            mappings[normalized] = relative
    return mappings

def _java_web_xml_route_mappings(root: Path, candidates: set[Path]) -> dict[str, str]:
    web_xml = root / "WEB-INF" / "web.xml"
    if not web_xml.is_file():
        return {}
    content = web_xml.read_text(encoding="utf-8", errors="ignore")
    servlet_classes: dict[str, str] = {}
    for block in re.findall(r"<servlet(?!-)\b.*?</servlet>", content, re.I | re.S):
        name_match = re.search(r"<servlet-name>\s*([^<]+?)\s*</servlet-name>", block, re.I)
        class_match = re.search(r"<servlet-class>\s*([^<]+?)\s*</servlet-class>", block, re.I)
        if name_match and class_match:
            servlet_classes[name_match.group(1).strip()] = class_match.group(1).strip()

    mappings: dict[str, str] = {}
    for block in re.findall(r"<servlet-mapping\b.*?</servlet-mapping>", content, re.I | re.S):
        name_match = re.search(r"<servlet-name>\s*([^<]+?)\s*</servlet-name>", block, re.I)
        pattern_match = re.search(r"<url-pattern>\s*([^<]+?)\s*</url-pattern>", block, re.I)
        if not name_match or not pattern_match:
            continue
        class_name = servlet_classes.get(name_match.group(1).strip())
        if not class_name:
            continue
        suffix = Path(*class_name.split(".")).with_suffix(".java").as_posix()
        matches = [candidate for candidate in candidates if candidate.as_posix().endswith(suffix)]
        if not matches:
            continue
        preferred = sorted(matches, key=lambda item: ("instrumented" in item.as_posix().casefold(), len(item.as_posix())))[0]
        normalized = pattern_match.group(1).strip().lstrip("/") or "./"
        mappings[normalized] = _relative(preferred, root)
    return mappings


def build_static_graph(
    target: TargetConfig,
    dynamic_nodes: list[str],
    skip_dirs: list[str] | None = None,
) -> dict[str, Any]:
    root = target.source_root.resolve()
    extensions = SOURCE_EXTENSIONS.get(target.language)
    if not extensions:
        raise ValueError(f"unsupported source language: {target.language}")
    files = _files(root, extensions, skip_dirs or [".git", "node_modules", "vendor", "venv", ".venv"])
    candidates = set(files)
    dependency_edges: set[tuple[str, str]] = set()
    http_edges: set[tuple[str, str]] = set()
    url_to_source: dict[str, str] = {}
    route_url_to_source: dict[str, str] = {}
    http_url_to_source: dict[str, str] = {}
    direct_url_to_source: dict[str, str] = {}

    public_extensions = tuple(str(item).lower() for item in target.public_extensions)

    for path in files:
        relative = _relative(path, root)
        if path.suffix.lower() in public_extensions and not _is_component_like(relative):
            direct_url_to_source[relative] = relative

        route_mappings = _route_mappings(path, target.language, relative, root, candidates)
        route_url_to_source.update(route_mappings)

        http_mappings = _http_target_mappings(path, root, candidates, relative, public_extensions)
        http_url_to_source.update(http_mappings)
        for target_url, target_source in http_mappings.items():
            http_edges.add((relative, target_source))

        if target.language == "php":
            targets = _php_edges(path, root, candidates)
        elif target.language == "python":
            targets = _python_edges(path, root, candidates)
        elif target.language == "go":
            targets = _go_edges(path, root, candidates)
        else:
            targets = _java_edges(path, root, candidates)
        dependency_edges.update((relative, _relative(target_path, root)) for target_path in targets)

    if target.language in {"java", "jsp"}:
        route_url_to_source.update(_java_web_xml_route_mappings(root, candidates))

    # A UP is an independent HTTP resource: direct public entry, framework route,
    # or target of a hyperlink/redirection/request.  If a file satisfies both UP
    # and CP evidence, UP takes precedence while static relationships are kept.
    url_to_source.update(direct_url_to_source)
    url_to_source.update(route_url_to_source)
    url_to_source.update(http_url_to_source)

    static_up_pages = set(url_to_source)
    static_up_sources = set(url_to_source.values())
    all_sources = {_relative(path, root) for path in files}
    cp_sources = sorted(all_sources - static_up_sources)

    dynamic_base_pages = {page.split("?", 1)[0].lstrip("/") for page in dynamic_nodes}
    up_prime0 = sorted(page for page in static_up_pages if page.split("?", 1)[0].lstrip("/") in dynamic_base_pages)
    remaining_up = sorted(static_up_pages - set(up_prime0))

    all_edges = dependency_edges | http_edges
    connected_sources: set[str] = set()
    for left, right in all_edges:
        connected_sources.add(left)
        connected_sources.add(right)

    standalone_up = {page for page in remaining_up if STANDALONE_ENTRY_PATTERN.search(page)}
    updiff1 = sorted(
        page for page in remaining_up
        if page not in standalone_up and url_to_source.get(page) in connected_sources
    )
    updiff2 = sorted(page for page in remaining_up if page not in set(updiff1))
    updiff = sorted(set(updiff1) | set(updiff2))

    observed_sources = {url_to_source[page] for page in up_prime0 if page in url_to_source}
    adjacency: dict[str, set[str]] = {}
    for left, right in dependency_edges:
        adjacency.setdefault(left, set()).add(right)
    reachable = set(observed_sources)
    queue = list(observed_sources)
    while queue:
        node = queue.pop()
        for neighbor in adjacency.get(node, set()):
            if neighbor not in reachable:
                reachable.add(neighbor)
                queue.append(neighbor)

    classifications = {
        # New paper-aligned resource sets.
        "UP": sorted(static_up_pages),
        "CP": cp_sources,
        "UP_prime0": up_prime0,
        "UPdiff1": updiff1,
        "UPdiff2": updiff2,
        "UPdiff": updiff,
        # Backward-compatible source-level summaries.
        "observed": sorted(observed_sources),
        "internal_reachable": sorted(reachable - observed_sources),
        "public_unobserved": updiff,
        "support_unreachable": sorted(all_sources - reachable - static_up_sources),
    }

    edge_rows = [
        {"from": left, "to": right, "kind": "dependency"}
        for left, right in sorted(dependency_edges)
    ] + [
        {"from": left, "to": right, "kind": "http"}
        for left, right in sorted(http_edges - dependency_edges)
    ]

    return {
        # N1 = UP'0 ? UPdiff ? CP.  UP nodes are URL nodes; CP nodes are source nodes.
        "nodes": sorted(set(up_prime0) | set(updiff) | set(cp_sources)),
        "source_nodes": sorted(all_sources),
        "edges": edge_rows,
        "dependency_edges": [{"from": left, "to": right} for left, right in sorted(dependency_edges)],
        "http_edges": [{"from": left, "to": right} for left, right in sorted(http_edges)],
        "url_to_source": dict(sorted(url_to_source.items())),
        "route_url_to_source": dict(sorted(route_url_to_source.items())),
        "http_url_to_source": dict(sorted(http_url_to_source.items())),
        "direct_url_to_source": dict(sorted(direct_url_to_source.items())),
        "classifications": classifications,
    }
