from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from ..config import PipelineConfig, RoleConfig
from ..database import Snapshot
from ..database_probe import create_database_probe
from ..errors import DatabaseError
from ..models import AttackVector, Finding, RequestSpec, RoleCrawl
from ..progress import progress
from .denials import extract_source_denial_markers


def _compact(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", "", value, flags=re.I | re.S)
    return re.sub(r"\s+", " ", value)[:200_000]


class ActiveDetector:
    def __init__(
        self,
        config: PipelineConfig,
        snapshot: Snapshot,
        session_factory=None,
        probe_factory=create_database_probe,
    ):
        self.config = config
        self.snapshot = snapshot
        self.session_factory = session_factory
        self.probe_factory = probe_factory
        self._probe_instance = None
        oracle = config.analysis.get("oracle", {})
        self.confirm_get_read = bool(oracle.get("confirm_get_read", True))
        self.use_login_form_denial = bool(oracle.get("login_form_denial", True))
        self.restore_after_each_attack = bool(oracle.get("restore_after_each_attack", False))
        self.timeout = float(oracle.get("timeout", 10))
        self.denied_statuses = set(oracle.get("denied_statuses", [401, 403]))
        configured_deny_markers = [
            str(item)
            for item in oracle.get("deny_markers", [])
        ]
        if oracle.get("extract_source_deny_markers", True):
            configured_deny_markers.extend(
                extract_source_denial_markers(
                    config.target.source_root,
                    config.crawl.get("skip_source_dirs", []),
                )
            )
        self.deny_markers = list(dict.fromkeys(str(item).casefold() for item in configured_deny_markers if str(item)))
        default_invalid_resource_markers = [
            "you seem to have followed an invalid address",
            "please be sure the specified post exists",
            "specified post exists",
            "specified thread does not exist",
            "specified forum does not exist",
        ]
        self.invalid_resource_markers = list(
            dict.fromkeys(
                str(item).casefold()
                for item in [*default_invalid_resource_markers, *oracle.get("invalid_resource_markers", [])]
                if str(item)
            )
        )
        self.login_markers = [
            str(item).casefold() for item in oracle.get("login_url_markers", ["login", "signin"])
        ]
        self.static_only_confirm_patterns = [
            re.compile(str(item), re.I) for item in oracle.get("static_only_confirm_patterns", [])
        ]
        self.public_page_patterns = [
            re.compile(str(item), re.I) for item in oracle.get("public_page_patterns", [])
        ]
        self.authenticated_public_page_patterns = [
            re.compile(str(item), re.I) for item in oracle.get("authenticated_public_page_patterns", [])
        ]
        self.redirect_markers = [
            str(item).casefold()
            for item in oracle.get(
                "redirect_markers",
                ["login", "signin", "warning", "warn", "error", "denied", "forbidden", "nopermission"],
            )
        ]
        self.write_success_redirect_is_vulnerable = bool(
            oracle.get("write_success_redirect_is_vulnerable", False)
        )
        self.write_success_redirect_patterns = [
            re.compile(str(item), re.I) for item in oracle.get("write_success_redirect_patterns", [])
        ]
        # A redirect is a denial only when its target is clearly a login/error/forbidden page.
        # Business-success redirects, especially JavaScript/meta refresh redirects back to list/edit pages,
        # must not be treated as access-control enforcement.
        self.force_static_pages = {
            str(item).split("?", 1)[0].lstrip("/").casefold()
            for item in config.analysis.get("force_static_pages", [])
        }
        self.csrf_token_parameters = {
            str(item)
            for item in oracle.get(
                "csrf_token_parameters",
                ["csrfmiddlewaretoken", "csrf_token", "_csrf", "_token", "authenticity_token"],
            )
            if str(item)
        }
        self.add_missing_csrf_tokens = bool(oracle.get("add_missing_csrf_tokens", True))

    def _probe(self):
        if self._probe_instance is None:
            self._probe_instance = self.probe_factory(self.config.database)
        return self._probe_instance

    def _apply_pre_detection_sql(self) -> None:
        sql_items = self.config.analysis.get("pre_detection_sql", [])
        if isinstance(sql_items, str):
            sql_items = [sql_items]
        if not sql_items:
            return
        probe = self._probe()
        executed = 0
        for sql in sql_items:
            text = str(sql).strip()
            if not text:
                continue
            probe.execute(text)
            executed += 1
        if executed:
            progress(f"pre-detection database seed SQL executed: {executed}")


    def _login_steps(self, login: dict[str, Any]) -> list[dict[str, Any]]:
        steps = login.get("steps")
        if isinstance(steps, list):
            return [dict(step) for step in steps if isinstance(step, dict)]
        return [login]

    def _hidden_form_fields(self, html: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for match in re.finditer(r"<input\b[^>]*>", html, re.I):
            tag = match.group(0)
            if not re.search(r"\btype\s*=\s*['\"]?hidden\b", tag, re.I):
                continue
            name_match = re.search(r"\bname\s*=\s*['\"]([^'\"]+)['\"]", tag, re.I)
            if not name_match:
                name_match = re.search(r"\bname\s*=\s*([^\s>]+)", tag, re.I)
            if not name_match:
                continue
            value_match = re.search(r"\bvalue\s*=\s*['\"]([^'\"]*)['\"]", tag, re.I)
            if not value_match:
                value_match = re.search(r"\bvalue\s*=\s*([^\s>]*)", tag, re.I)
            fields[name_match.group(1)] = value_match.group(1) if value_match else ""
        return fields

    def _session(self, role: RoleConfig | None):
        if self.session_factory is None:
            import requests

            session = requests.Session()
        else:
            session = self.session_factory()
        session.headers.update({"User-Agent": "DRHL/1.0 access-control verifier"})
        if role is None:
            return session
        session.headers.update(role.headers)
        session.cookies.update(role.cookies)
        login = role.http_login
        if login:
            for step in self._login_steps(login):
                target = step.get("post_url") or step.get("url")
                if not target:
                    continue
                base = self.config.target.base_url.rstrip("/") + "/"
                method = str(step.get("method", "POST")).upper()
                headers = dict(step.get("headers", {}))
                data = dict(step.get("data", {}))
                if method == "POST" and step.get("url") and step.get("post_url"):
                    visit_url = urljoin(base, str(step["url"]))
                    visit_response = session.get(visit_url, headers=headers, timeout=self.timeout)
                    visit_response.raise_for_status()
                    if step.get("include_form_fields", True):
                        data = {**self._hidden_form_fields(visit_response.text or ""), **data}
                url = urljoin(base, str(target))
                response = session.request(
                    method,
                    url,
                    data=data,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=bool(step.get("allow_redirects", True)),
                )
                response.raise_for_status()
        return session


    def _role_username(self, role: RoleConfig | None) -> str | None:
        if role is None or not role.http_login:
            return None
        for step in self._login_steps(role.http_login):
            data = step.get("data", {})
            if not isinstance(data, dict):
                continue
            for key in ("quick_username", "username", "login", "user", "email"):
                value = data.get(key)
                if value:
                    return str(value)
        return None

    def _mybb_user_value(self, role: RoleConfig | None, field: str) -> str | None:
        username = self._role_username(role)
        if not username:
            return None
        table = "mybb_users"
        if field != "MD5(CONCAT(loginkey,salt,regdate))" and not re.fullmatch(r"[A-Za-z0-9_]+", field):
            return None
        escaped = username.replace("\\", "\\\\").replace("'", "\\'")
        return self._probe().scalar(f"SELECT {field} FROM {table} WHERE username='{escaped}' LIMIT 1") or None

    def _runtime_token(self, name: str, role: RoleConfig | None) -> str | None:
        if name == "my_post_key" and self.config.database.get("database") == "mybb":
            return self._mybb_user_value(role, "MD5(CONCAT(loginkey,salt,regdate))")
        return None

    def _apply_runtime_tokens(self, params: dict[str, Any], role: RoleConfig | None) -> dict[str, Any]:
        updated = dict(params)
        for key in list(updated):
            token = self._runtime_token(str(key), role)
            if token:
                updated[key] = token
        return updated

    def _refresh_form_tokens(
        self,
        session,
        page: str,
        request: RequestSpec,
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        if not self.csrf_token_parameters:
            return params
        base = self.config.target.base_url.rstrip() + "/"
        candidates: list[str] = []
        for candidate in (request.referer, page):
            if not candidate:
                continue
            candidate_url = urljoin(base, str(candidate).lstrip("/"))
            if candidate_url not in candidates:
                candidates.append(candidate_url)
        if not candidates:
            return params

        token_names_lower = {name.casefold() for name in self.csrf_token_parameters}
        existing_token_names = {str(key) for key in params if str(key).casefold() in token_names_lower}
        for candidate_url in candidates:
            try:
                response = session.get(candidate_url, headers=headers, timeout=self.timeout, allow_redirects=True)
            except Exception:
                continue
            fields = self._hidden_form_fields(response.text or "")
            if not fields:
                continue
            by_lower = {str(key).casefold(): (str(key), value) for key, value in fields.items()}
            refreshed = dict(params)
            changed = False
            for token_name in sorted(token_names_lower):
                field = by_lower.get(token_name)
                if not field:
                    continue
                actual_name, value = field
                target_names = [name for name in existing_token_names if name.casefold() == token_name]
                if target_names:
                    for target_name in target_names:
                        refreshed[target_name] = value
                        changed = True
                elif self.add_missing_csrf_tokens:
                    refreshed[actual_name] = value
                    changed = True
            if changed:
                return refreshed
        return params

    def _template(self, value: Any, context: dict[str, str]) -> Any:
        if isinstance(value, str):
            return re.sub(r"\{\{([^{}]+)\}\}", lambda match: context.get(match.group(1), match.group(0)), value)
        if isinstance(value, dict):
            return {key: self._template(item, context) for key, item in value.items()}
        if isinstance(value, list):
            return [self._template(item, context) for item in value]
        return value

    def _send(
        self,
        session,
        page: str,
        request: RequestSpec,
        overrides: dict[str, Any] | None = None,
        role: RoleConfig | None = None,
    ):
        params = dict(request.params)
        if overrides:
            for key, value in overrides.items():
                params[key] = value
        params = self._apply_runtime_tokens(params, role)
        url = urljoin(self.config.target.base_url.rstrip("/") + "/", page.lstrip("/"))
        headers = {}
        if request.referer:
            headers["Referer"] = urljoin(
                self.config.target.base_url.rstrip("/") + "/", request.referer.lstrip("/")
            )
        method = request.method if request.method != "UNKNOWN" else "GET"
        if method == "GET":
            parsed = urlsplit(url)
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            query.update(params)
            url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query, doseq=True), ""))
            return session.get(url, headers=headers, timeout=self.timeout, allow_redirects=False)
        params = self._refresh_form_tokens(session, page, request, params, headers)
        return session.request(method, url, data=params, headers=headers, timeout=self.timeout, allow_redirects=False)

    def _redirect_location(self, response) -> str | None:
        location = response.headers.get("Location") or response.headers.get("location")
        if not location:
            return None
        return urljoin(str(response.url), str(location))

    def _body_redirect_target(self, response) -> str | None:
        content = str(response.text or "")
        base_url = str(response.url)
        for meta in re.finditer(r"<meta\b[^>]*>", content, re.I | re.S):
            tag = meta.group(0)
            if not re.search(r'http-equiv\s*=\s*([\'"]?)\s*refresh\s*\1', tag, re.I):
                continue
            content_match = re.search(
                r'content\s*=\s*(?:[\'"](?P<quoted>[^\'"]*)[\'"]|(?P<bare>[^\s>]+))',
                tag,
                re.I | re.S,
            )
            if not content_match:
                continue
            refresh = (content_match.group("quoted") or content_match.group("bare") or "").strip()
            target_match = re.search(r"(?:^|;)\s*url\s*=\s*([^;]+)\s*$", refresh, re.I)
            if not target_match:
                continue
            delay_text = refresh.split(";", 1)[0].strip()
            try:
                delay = float(delay_text) if delay_text else 0.0
            except ValueError:
                delay = 0.0
            target = target_match.group(1).strip().strip('\"\'')
            if target and delay <= 1.0:
                return urljoin(base_url, target)

        executable_js: list[str] = []
        executable_js.extend(
            match.group(1)
            for match in re.finditer(r"<script\b[^>]*>(.*?)</script>", content, re.I | re.S)
        )
        for match in re.finditer(
            r'<(?:body|html)\b[^>]*\sonload\s*=\s*(?:(?P<quote>[\'"])(?P<quoted>.*?)(?P=quote)|(?P<bare>[^\s>]+))',
            content,
            re.I | re.S,
        ):
            executable_js.append(match.group("quoted") or match.group("bare") or "")

        js_patterns = [
            r'(?:window\.)?location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'(?:window\.)?location\.(?:replace|assign)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'document\.location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
        ]
        for script in executable_js:
            for pattern in js_patterns:
                match = re.search(pattern, script, re.I | re.S)
                if match:
                    return urljoin(base_url, match.group(1).strip())
        return None

    def _looks_like_login_form(self, response) -> bool:
        content = str(response.text or "")
        if not re.search(r"<form\b", content, re.I):
            return False
        has_password = re.search(r"<input[^>]+(?:type|name)=[\"']?password\b", content, re.I) is not None
        if not has_password:
            return False

        login_markers = [*self.login_markers, "login", "signin", "sign-in", "logon"]
        current_url = str(getattr(response, "url", "") or "").casefold()
        if any(marker and marker in current_url for marker in login_markers):
            return True

        for match in re.finditer(r"<form\b[^>]*>", content, re.I):
            tag = match.group(0)
            action_match = re.search(r"\baction\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
            if not action_match:
                continue
            action = action_match.group(2).strip().casefold()
            if any(marker and marker in action for marker in login_markers):
                return True

        return False

    def _page_match_targets(self, vector: AttackVector) -> list[str]:
        targets = [vector.page]
        parsed = urlsplit(vector.page)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        for key, value in vector.request.params.items():
            if isinstance(value, (dict, list)):
                continue
            query[str(key)] = str(value)
        if query:
            effective = urlunsplit(("", "", parsed.path, urlencode(query, doseq=True), ""))
            if effective not in targets:
                targets.append(effective)
        return targets

    def _is_public_page(self, vector: AttackVector) -> bool:
        return any(
            pattern.search(target)
            for target in self._page_match_targets(vector)
            for pattern in self.public_page_patterns
        )

    def _is_authenticated_public_page(self, vector: AttackVector, actor: RoleConfig | None) -> bool:
        if actor is None or actor.kind == "visitor":
            return False
        return any(
            pattern.search(target)
            for target in self._page_match_targets(vector)
            for pattern in self.authenticated_public_page_patterns
        )

    # Java exception trace patterns that indicate a server-side error
    # (e.g. NullPointerException when session attributes are null),
    # NOT a successful unauthorized access.
    _JAVA_EXCEPTION_PATTERN = re.compile(
        r"(?:java|javax|jakarta)\.\w+(?:\.\w+)?\.(\w+Exception|\\w+Error)",
        re.I,
    )
    _JAVA_STACK_TRACE_PATTERN = re.compile(
        r"(?m)^\s+at\s+(?:java|javax|jakarta|forum|org|com|net)\.",
        re.I,
    )

    @staticmethod
    def _has_java_exception_trace(text: str) -> bool:
        """Return True when *text* looks like a Java exception / stack trace dump."""
        if not text or not text.strip():
            return False
        if ActiveDetector._JAVA_EXCEPTION_PATTERN.search(text):
            return True
        # A stack trace typically has at least 2-3 "at …" lines.
        stack_lines = ActiveDetector._JAVA_STACK_TRACE_PATTERN.findall(text)
        return len(stack_lines) >= 2

    @staticmethod
    def _body_length_after_trim(text: str) -> int:
        """Return the length of *text* after stripping whitespace and common
        boilerplate (script/style tags, HTML comments)."""
        if not text:
            return 0
        cleaned = re.sub(r"<script\b.*?</script>", "", text, flags=re.I | re.S)
        cleaned = re.sub(r"<style\b.*?</style>", "", cleaned, flags=re.I | re.S)
        cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.S)
        cleaned = cleaned.strip()
        return len(cleaned)

    def _redirect_match_targets(self, response) -> list[str]:
        target = self._redirect_location(response) or self._body_redirect_target(response)
        if not target:
            return []
        targets = [target]
        base = self.config.target.base_url.rstrip("/") + "/"
        if target.startswith(base):
            targets.append(target[len(base):])
        parsed = urlsplit(target)
        relative_path = parsed.path.lstrip("/")
        base_path = urlsplit(base).path.strip("/")
        if base_path and relative_path.startswith(base_path + "/"):
            relative_path = relative_path[len(base_path) + 1:]
        if relative_path:
            targets.append(relative_path + (("?" + parsed.query) if parsed.query else ""))
        return list(dict.fromkeys(targets))

    def _is_configured_write_success_redirect(self, vector: AttackVector, response) -> bool:
        if not self.write_success_redirect_is_vulnerable:
            return False
        if vector.request.method.upper() == "GET":
            return False
        if not (300 <= response.status_code < 400):
            return False
        if not self.write_success_redirect_patterns:
            return False
        return any(
            pattern.search(target)
            for target in self._redirect_match_targets(response)
            for pattern in self.write_success_redirect_patterns
        )

    def _denial(self, response) -> list[str]:
        evidence = []
        if response.status_code in self.denied_statuses:
            evidence.append(f"HTTP {response.status_code}")
        http_redirect_target = self._redirect_location(response)
        body_redirect_target = self._body_redirect_target(response)
        redirect_target = http_redirect_target or body_redirect_target
        if redirect_target:
            target = redirect_target.casefold()
            if any(marker in target for marker in [*self.login_markers, *self.redirect_markers]):
                evidence.append(f"denial redirect: {redirect_target}")
        if any(marker in str(response.url).casefold() for marker in self.login_markers):
            evidence.append(f"authentication page: {response.url}")
        content = str(response.text or "").casefold()
        marker = next((item for item in self.deny_markers if item in content), None)
        if marker:
            evidence.append(f"denial marker: {marker}")
        if re.search(r"history\.back\s*\(", str(response.text or ""), re.I):
            evidence.append("client-side denial: history.back()")
        if self.use_login_form_denial and self._looks_like_login_form(response):
            evidence.append("login form in response")
        # Detect Java exception / stack trace in the response body.
        # A NullPointerException (e.g. from a null session attribute) means the
        # access-control check *did* run and prevented execution — it is NOT a
        # successful bypass.  Likewise an empty body is strong evidence that the
        # server-side handler aborted early (common in silent-catch patterns).
        response_text = str(response.text or "")
        if self._has_java_exception_trace(response_text):
            evidence.append("Java exception trace in response body")
        elif self._body_length_after_trim(response_text) == 0 and response.status_code == 200:
            evidence.append("empty response body (possible silent exception)")
        return evidence

    def _invalid_resource(self, response) -> list[str]:
        content = _compact(str(response.text or "")).casefold()
        marker = next((item for item in self.invalid_resource_markers if item in content), None)
        if marker:
            return [f"invalid resource marker: {marker}"]
        return []

    def _protected_content_markers(self, vector: AttackVector) -> list[str]:
        markers: list[str] = []
        raw_rules = self.config.analysis.get("oracle", {}).get("protected_content_markers", [])
        candidates = [str(vector.page), str(vector.page).split("?", 1)[0]]
        for raw in raw_rules:
            if isinstance(raw, str):
                marker = raw.strip()
                if marker:
                    markers.append(marker)
                continue
            if not isinstance(raw, dict):
                continue
            pattern = str(raw.get("pattern") or "")
            if pattern:
                matched = None
                for candidate in candidates:
                    matched = re.search(pattern, candidate, re.I)
                    if matched:
                        break
                if not matched:
                    continue
                group = raw.get("marker_group", raw.get("group", 1))
                try:
                    marker = matched.group(int(group))
                except Exception:
                    marker = ""
            else:
                marker = str(raw.get("marker") or "")
            marker = marker.strip()
            if marker:
                markers.append(marker)
        return list(dict.fromkeys(markers))

    def _protected_content_absent(self, vector: AttackVector, response) -> list[str]:
        markers = self._protected_content_markers(vector)
        if not markers or response.status_code != 200:
            return []
        content = _compact(str(response.text or "")).casefold()
        missing = [marker for marker in markers if marker.casefold() not in content]
        if missing and len(missing) == len(markers):
            return ["protected content marker absent after attack: " + ", ".join(missing[:3])]
        return []

    def _verify_response(self, vector: AttackVector, actor: RoleConfig | None, authorized: RoleConfig | None) -> Finding:
        actor_name = actor.name if actor else "visitor"
        evidence = ["oracle=response-cascade"]
        if self._is_public_page(vector):
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                "not_vulnerable",
                "high",
                vector.request.method,
                None,
                [*evidence, "configured public page; successful access is not a vulnerability"],
            )
        if vector.category != "horizontal" and self._is_authenticated_public_page(vector, actor):
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                "not_vulnerable",
                "high",
                vector.request.method,
                None,
                [*evidence, "configured authenticated-public page; ordinary authenticated users are allowed"],
            )
        try:
            session = self._session(actor)
            try:
                response = self._send(session, vector.page, vector.request, role=actor)
            finally:
                session.close()
            denial = self._denial(response)
            invalid_resource = self._invalid_resource(response)
            evidence.extend(denial)
            evidence.extend(invalid_resource)
            protected_absent = self._protected_content_absent(vector, response)
            if invalid_resource:
                status, confidence = "not_vulnerable", "high"
                evidence.append("target resource did not exist; access-control vulnerability is not confirmed")
            elif protected_absent:
                status, confidence = "not_vulnerable", "high"
                evidence.extend(protected_absent)
                evidence.append("protected resource content was not exposed to the attacking actor")
            elif denial:
                status, confidence = "not_vulnerable", "high"
            elif self._is_configured_write_success_redirect(vector, response):
                location = self._redirect_location(response)
                status, confidence = "vulnerable", "high"
                evidence = [item for item in evidence if not item.startswith("denial redirect:")]
                evidence.append(
                    f"write request accepted with configured success redirect: {location or response.status_code}"
                )
            elif vector.category == "static_only":
                if not str(response.text or "").strip():
                    status, confidence = "not_vulnerable", "high"
                    evidence.append("static page response body was empty; treated as not vulnerable")
                elif (
                    self.static_only_confirm_patterns
                    and vector.page.split("?", 1)[0].lstrip("/").casefold() not in self.force_static_pages
                    and not any(pattern.search(vector.page) for pattern in self.static_only_confirm_patterns)
                ):
                    status, confidence = "not_vulnerable", "high"
                    evidence.append("static-only page did not match configured high-risk standalone patterns")
                elif response.status_code == 200 and not denial:
                    status, confidence = "vulnerable", "high"
                    evidence.append("HTTP 200 without redirect or denial marker")
                else:
                    status, confidence = "not_vulnerable", "high"
            elif response.status_code == 200 and not denial:
                # Defence-in-depth: a nearly-empty body on a non-GET request
                # is almost certainly a silent exception, not a real bypass.
                body_len = self._body_length_after_trim(str(response.text or ""))
                if vector.category != "static_only" and body_len < 100:
                    status, confidence = "not_vulnerable", "medium"
                    evidence.append(
                        f"HTTP 200 without denial marker but response body is nearly empty"
                        f" ({body_len} chars after trim); possible silent exception or missing"
                        f" access-control output — treat as not vulnerable"
                    )
                else:
                    status, confidence = "vulnerable", "high"
                    evidence.append("HTTP 200 without redirect or denial marker")
            elif (
                self.write_success_redirect_is_vulnerable
                and vector.request.method.upper() != "GET"
                and 300 <= response.status_code < 400
                and not denial
            ):
                location = self._redirect_location(response)
                status, confidence = "vulnerable", "high"
                evidence.append(
                    f"write request accepted with non-denial redirect: {location or response.status_code}"
                )
            else:
                status, confidence = "not_vulnerable", "high"
                if 300 <= response.status_code < 400:
                    location = self._redirect_location(response)
                    evidence.append(f"redirected: {location or response.status_code}")
                elif response.status_code != 200:
                    evidence.append(f"HTTP {response.status_code}; attack did not receive a normal resource page")
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                status,
                confidence,
                vector.request.method,
                response.status_code,
                evidence,
            )
        except DatabaseError:
            raise
        except Exception as exc:
            return self._error(vector, actor_name, "response", exc)
        finally:
            self._restore_after_attack("after a response-oracle attack request")

    def _restore(self, context: str) -> None:
        try:
            self.snapshot.restore()
        except Exception as exc:
            raise DatabaseError(f"database restore failed {context}; detection stopped") from exc

    def _restore_after_attack(self, context: str) -> None:
        if self.restore_after_each_attack:
            self._restore(context)

    def _error(self, vector: AttackVector, actor: str, operation: str, exc: Exception) -> Finding:
        return Finding(
            vector.category,
            vector.page,
            actor,
            "not_vulnerable",
            "none",
            vector.request.method,
            None,
            [f"operation={operation}"],
            str(exc),
        )

    def _verify_read(
        self, vector: AttackVector, actor: RoleConfig | None, authorized: RoleConfig | None
    ) -> Finding:
        baseline = None
        actor_name = actor.name if actor else "visitor"
        if vector.category != "static_only" and vector.request.method.upper() == "GET" and not self.confirm_get_read:
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                "not_vulnerable",
                "high",
                vector.request.method,
                None,
                ["oracle=response-read", "GET read response oracle is disabled by configuration"],
            )
        if (
            vector.category != "static_only"
            and vector.request.method.upper() == "GET"
            and self.confirm_get_read_patterns
            and not any(pattern.search(vector.page) for pattern in self.confirm_get_read_patterns)
        ):
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                "not_vulnerable",
                "high",
                vector.request.method,
                None,
                ["oracle=response-read", "GET read response oracle is limited to configured page patterns"],
            )
        try:
            if authorized is not None:
                session = self._session(authorized)
                try:
                    baseline = self._send(session, vector.page, vector.request, role=authorized)
                finally:
                    session.close()
                self._restore_after_attack("after the authorized read baseline")
            session = self._session(actor)
            try:
                response = self._send(session, vector.page, vector.request, role=actor)
            finally:
                session.close()
            denial = self._denial(response)
            invalid_resource = self._invalid_resource(response)
            evidence = ["oracle=response-read", *denial, *invalid_resource]
            protected_absent = self._protected_content_absent(vector, response)
            accessible = 200 <= response.status_code < 400 and not denial and not invalid_resource and not protected_absent
            if invalid_resource:
                status, confidence = "not_vulnerable", "high"
                evidence.append("target resource did not exist; access-control vulnerability is not confirmed")
            elif protected_absent:
                status, confidence = "not_vulnerable", "high"
                evidence.extend(protected_absent)
                evidence.append("protected resource content was not exposed to the attacking actor")
            elif vector.category == "static_only":
                if not str(response.text or "").strip():
                    status, confidence = "not_vulnerable", "high"
                    evidence.append("static page response body was empty; treated as not vulnerable")
                elif (
                    self.static_only_confirm_patterns
                    and vector.page.split("?", 1)[0].lstrip("/").casefold() not in self.force_static_pages
                    and not any(pattern.search(vector.page) for pattern in self.static_only_confirm_patterns)
                ):
                    status, confidence = "not_vulnerable", "high"
                    evidence.append("static-only page did not match configured high-risk standalone patterns")
                elif accessible:
                    status, confidence = "vulnerable", "high"
                    evidence.append("static page was directly accessible to a visitor and no denial marker was observed")
                else:
                    status, confidence = "not_vulnerable", "high"
            elif vector.request.method.upper() == "GET" and not self.confirm_get_read:
                status, confidence = "not_vulnerable", "high"
                evidence.append("GET read response oracle is disabled by configuration")
            elif baseline is None:
                status = "not_vulnerable"
                confidence = "low"
                evidence.append("no authorized response baseline; treated as not vulnerable by binary reporting policy")
            elif accessible:
                status, confidence = "vulnerable", "high"
                evidence.append("attack response was accessible and no denial marker was observed")
            else:
                status, confidence = "not_vulnerable", "high"
            return Finding(
                vector.category,
                vector.page,
                actor_name,
                status,
                confidence,
                vector.request.method,
                response.status_code,
                evidence,
            )
        except DatabaseError:
            raise
        except Exception as exc:
            return self._error(vector, actor_name, "read", exc)
        finally:
            self._restore_after_attack("after a read attack request")

    def _role_for_crawl(self, crawl: RoleCrawl) -> RoleConfig | None:
        roles = {role.name: role for role in self.config.roles}
        return roles.get(crawl.role)

    def _configured_attackers(self, category: str, default: list[RoleConfig | None]) -> list[RoleConfig | None]:
        configured = self.config.analysis.get("attacker_roles", {})
        if not isinstance(configured, dict) or category not in configured:
            return default
        raw_names = configured.get(category, [])
        if isinstance(raw_names, str):
            raw_names = [raw_names]
        roles = {role.name: role for role in self.config.roles}
        attackers: list[RoleConfig | None] = []
        for raw_name in raw_names:
            name = str(raw_name).strip()
            if not name:
                continue
            if name.casefold() == "visitor":
                attackers.append(None)
            elif name in roles:
                attackers.append(roles[name])
        return attackers or default

    def _verify(
        self,
        vector: AttackVector,
        actor: RoleConfig | None,
        authorized: RoleConfig | None,
        horizontal_overrides: dict[str, Any] | None = None,
        page_override: str | None = None,
    ) -> Finding:
        request = vector.request
        if horizontal_overrides:
            request = RequestSpec(
                request.method,
                {**request.params, **horizontal_overrides},
                request.referer,
            )
        page = page_override or vector.page
        if page_override and request.referer == vector.page:
            request = RequestSpec(request.method, request.params, page_override)
        if horizontal_overrides or page_override:
            vector = AttackVector(
                vector.category,
                page,
                vector.authorized_roles,
                request,
                vector.identity_parameters,
                vector.page_overrides,
            )
        progress("verification oracle: response-cascade")
        return self._verify_response(vector, actor, authorized)

    def run(self, vectors: list[AttackVector]) -> list[Finding]:
        roles = {role.name: role for role in self.config.roles}
        admins = [role for role in self.config.roles if role.kind == "admin"]
        users = [role for role in self.config.roles if role.kind == "user"]
        findings = []
        horizontal_values = dict(self.config.analysis.get("horizontal_overrides", {}))

        try:
            self._apply_pre_detection_sql()
            progress(f"starting active verification for {len(vectors)} attack vectors")
            for index, vector in enumerate(vectors, 1):
                progress(f"[detect {index}/{len(vectors)}] {vector.category}: {vector.page}")
                authorized = next((roles[name] for name in vector.authorized_roles if name in roles), None)
                before = len(findings)
                if vector.category == "static_only":
                    findings.append(self._verify(vector, None, None))
                elif vector.category == "authenticated_only":
                    for attacker in self._configured_attackers("authenticated_only", [None]):
                        findings.append(self._verify(vector, attacker, authorized))
                elif vector.category == "admin_only":
                    admin = authorized or (admins[0] if admins else None)
                    default_attackers: list[RoleConfig | None] = [None, *users]
                    for attacker in self._configured_attackers("admin_only", default_attackers):
                        findings.append(self._verify(vector, attacker, admin))
                elif vector.category == "vertical":
                    admin = authorized or (admins[0] if admins else None)
                    default_attackers = [users[0]] if users else []
                    attackers = self._configured_attackers("vertical", default_attackers)
                    if attackers:
                        for attacker in attackers:
                            findings.append(self._verify(vector, attacker, admin))
                    else:
                        findings.append(
                            Finding(
                                vector.category,
                                vector.page,
                                "user",
                                "not_vulnerable",
                                "none",
                                vector.request.method,
                                None,
                                ["no ordinary user role was configured; treated as not vulnerable by binary reporting policy"],
                            )
                        )
                elif vector.category == "horizontal":
                    override_options: list[dict[str, Any]] = [{}]
                    for key in vector.identity_parameters:
                        if key not in horizontal_values:
                            continue
                        raw_value = horizontal_values[key]
                        values = raw_value if isinstance(raw_value, list) else [raw_value]
                        override_options = [
                            {**base, key: value}
                            for base in override_options
                            for value in values
                        ]
                    page_options = list(vector.page_overrides or []) or [None]
                    overrides_available = any(
                        key in horizontal_values for key in vector.identity_parameters
                    ) or bool(vector.page_overrides)
                    if not overrides_available:
                        findings.append(
                            Finding(
                                vector.category,
                                vector.page,
                                authorized.name if authorized else "user",
                                "not_vulnerable",
                                "none",
                                vector.request.method,
                                None,
                                ["no horizontal override value was configured; treated as not vulnerable by binary reporting policy"],
                            )
                        )
                    elif authorized is not None:
                        for page_override in page_options:
                            for overrides in override_options:
                                finding = self._verify(vector, authorized, authorized, overrides, page_override)
                                if overrides:
                                    finding.evidence.append(
                                        "horizontal override: "
                                        + ", ".join(f"{key}={value}" for key, value in sorted(overrides.items()))
                                    )
                                if page_override:
                                    finding.evidence.append(f"horizontal page override: {page_override}")
                                findings.append(finding)
                statuses = ", ".join(item.status for item in findings[before:]) or "no tests"
                progress(f"[detect {index}/{len(vectors)}] completed: {statuses}")
        finally:
            if not self.restore_after_each_attack:
                self._restore("after all attack vectors")
        return findings
