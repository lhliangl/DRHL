from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


SOURCE_EXTENSIONS = {
    ".php",
    ".phtml",
    ".html",
    ".htm",
    ".js",
    ".jsp",
    ".asp",
    ".aspx",
    ".py",
    ".go",
}

DENIAL_LITERAL_PATTERNS = (
    re.compile(r"(?:die|exit)\s*\(\s*(['\"])(.*?)\1\s*\)\s*;?", re.I | re.S),
    re.compile(r"echo\s+(['\"])(.*?)\1\s*;[^}]*?exit\s*\(\s*\)\s*;?", re.I | re.S),
)

PHP_LANGUAGE_LITERAL_PATTERN = re.compile(
    r"\$l\s*\[\s*(['\"])(?P<key>.*?)\1\s*\]\s*=\s*(['\"])(?P<message>.*?)\3\s*;",
    re.I | re.S,
)

PHP_VARIABLE_LITERAL_PATTERN = re.compile(
    r"\$(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['\"])(?P<message>.*?)\2\s*;",
    re.I | re.S,
)

GENERIC_STRING_LITERAL_PATTERN = re.compile(r"(['\"])(?P<message>[^'\"]{3,240})\1", re.S)

DENIAL_LANGUAGE_KEY_PATTERN = re.compile(
    r"(?:access[_-]?denied|no[_-]?permission|nopermission|permission[_-]?denied|not[_-]?authori[sz]ed|"
    r"error[_-]?no[_-]?perm|invalid[_-]?admin[_-]?session|enter[_-]?username[_-]?and[_-]?password|"
    r"error[_-]?invalid[_-]?username[_-]?password|login[_-]?failed|admin[_-]?login|cp[_-]?login[_-]?failed)",
    re.I,
)

DENIAL_MESSAGE_PATTERN = re.compile(
    r"(?:do not have permission|don't have permission|do not have access|don't have access|must be logged in|not logged in|please enter your username and password|"
    r"invalid administration session|username and password combination|access denied|not authorized|"
    r"permission denied|no permission|forbidden|login failed|email or password|username or password|"
    r"direct initialization of this file is not allowed|hacking attempt|invalid administration session|"
    r"you are not authorized|bad referer|invalid username or password|"
    r"你没有权限|没有权限|无权访问|未授权|请登录|需要登录|登录失败|用户名或密码)",
    re.I,
)


def _is_skipped(path: Path, root: Path, skip_source_dirs: Iterable[str]) -> bool:
    skip_parts = {str(item).casefold() for item in skip_source_dirs}
    if not skip_parts:
        return False
    try:
        relative = path.relative_to(root)
    except ValueError:
        relative = path
    return any(part.casefold() in skip_parts for part in relative.parts[:-1])


def _normalize_message(value: str) -> str | None:
    message = re.sub(r"\\(['\"])", r"\1", value)
    message = re.sub(r"<[^>]+>", " ", message)
    message = re.sub(r"\s+", " ", message).strip()
    if len(message) < 3:
        return None
    if "$" in message:
        return None
    if "{" in message or "}" in message:
        return None
    return message


def _looks_like_login_form_source(content: str) -> bool:
    if not re.search(r"<form\b", content, re.I):
        return False
    has_password = re.search(r"<input[^>]+(?:type|name)=[\"']?password\b", content, re.I) is not None
    has_login = re.search(r"(?:login|signin|登录|用户名|密码)", content, re.I) is not None
    return bool(has_password and has_login)


def extract_source_denial_markers(source_root: str | Path, skip_source_dirs: Iterable[str] = ()) -> list[str]:
    """Extract response denial text from source code.

    The primary signal mirrors the original DRHL behavior: literal messages
    emitted by `die(...)`, `exit(...)`, or `echo "..."; exit();` are treated
    as denial markers.

    PHP applications such as MyBB often render access-control failures through
    language-pack strings instead of direct termination calls. For those, this
    extractor also accepts PHP `$l['key'] = "message";` literals only when both
    the key and the message are explicitly access-control/login-denial related.
    Generic labels such as "password:" are intentionally not inferred.
    """

    root = Path(source_root)
    if not root.is_dir():
        return []

    markers: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in SOURCE_EXTENSIONS:
            continue
        if _is_skipped(path, root, skip_source_dirs):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in DENIAL_LITERAL_PATTERNS:
            for match in pattern.finditer(content):
                message = _normalize_message(match.group(2))
                if message and DENIAL_MESSAGE_PATTERN.search(message):
                    markers.setdefault(message.casefold(), message)
        if path.suffix.casefold() in {".php", ".phtml"}:
            for match in PHP_LANGUAGE_LITERAL_PATTERN.finditer(content):
                key = match.group("key")
                if not DENIAL_LANGUAGE_KEY_PATTERN.search(key):
                    continue
                message = _normalize_message(match.group("message"))
                if message and DENIAL_MESSAGE_PATTERN.search(message):
                    markers.setdefault(message.casefold(), message)
            for match in PHP_VARIABLE_LITERAL_PATTERN.finditer(content):
                key = match.group("key")
                if not DENIAL_LANGUAGE_KEY_PATTERN.search(key):
                    continue
                message = _normalize_message(match.group("message"))
                if message and DENIAL_MESSAGE_PATTERN.search(message):
                    markers.setdefault(message.casefold(), message)
        for match in GENERIC_STRING_LITERAL_PATTERN.finditer(content):
            message = _normalize_message(match.group("message"))
            if message and DENIAL_MESSAGE_PATTERN.search(message):
                markers.setdefault(message.casefold(), message)
    return sorted(markers.values(), key=str.casefold)


