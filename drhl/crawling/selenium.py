from __future__ import annotations

import hashlib
import json
import re
import time
from collections import deque
from urllib.parse import parse_qs, urljoin, urlsplit
from typing import Any

from ..config import PipelineConfig, RoleConfig
from ..io import write_json
from ..models import RequestSpec, RoleCrawl
from ..progress import progress
from .urls import absolute_url, canonical_page, in_scope, request_params


class SeleniumRoleCrawler:
    """Selenium 4 crawler with Chrome network-event collection."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.driver = None
        self._current_role: RoleConfig | None = None
        self._runtime_token_cache: dict[tuple[str, str], str] = {}

    def _secret_names(self) -> set[str]:
        return {
            str(item).casefold()
            for item in self.config.crawl.get(
                "secret_parameters", ["password", "passwd", "pwd", "token", "csrf", "_token"]
            )
        }

    def _redact_secret_parameters(self) -> bool:
        return bool(self.config.crawl.get("redact_secret_parameters", True))

    def _should_record_parameter(self, name: str) -> bool:
        if self._redact_secret_parameters() and name.casefold() in self._secret_names():
            return False
        ignored = {str(item).casefold() for item in self.config.crawl.get("ignore_form_parameters", [])}
        return name.casefold() not in ignored

    def _excluded_submit_names(self) -> set[str]:
        ignored = {str(item).casefold() for item in self.config.crawl.get("ignore_form_parameters", [])}
        ignored.update(str(item).casefold() for item in self.config.crawl.get("exclude_submit_names", []))
        return ignored

    def _excluded_submit_value_markers(self) -> list[str]:
        return [str(item).casefold() for item in self.config.crawl.get("exclude_submit_value_markers", [])]

    def _url_match_candidates(self, url: str, canonical: str | None = None) -> list[str]:
        base_url = self.config.target.base_url
        candidates = [url, absolute_url(base_url, url)]
        if canonical:
            candidates.append(canonical)
        else:
            try:
                candidates.append(canonical_page(url, base_url, list(self.config.crawl.get("preserve_query_parameters", [])), list(self.config.crawl.get("drop_query_parameters", [])), list(self.config.crawl.get("path_parameter_patterns", []))))
            except Exception:
                pass
        return candidates

    def _role_specific_values(self, key: str) -> list[str]:
        role = self._current_role
        if role is None:
            return []
        configured = self.config.crawl.get(f"{key}_by_role", {})
        if not isinstance(configured, dict):
            return []
        values: list[str] = []
        for lookup in (role.name, role.kind):
            raw = configured.get(lookup, [])
            if isinstance(raw, str):
                values.append(raw)
            elif isinstance(raw, list):
                values.extend(str(item) for item in raw)
        return values

    def _is_excluded_url(self, url: str) -> bool:
        markers = [str(value).casefold() for value in self.config.crawl.get("exclude_url_markers", ["logout", "logoff"])]
        markers.extend(value.casefold() for value in self._role_specific_values("exclude_url_markers"))
        if any(marker in url.casefold() for marker in markers):
            return True
        patterns = [str(value) for value in self.config.crawl.get("exclude_url_patterns", [])]
        patterns.extend(self._role_specific_values("exclude_url_patterns"))
        if not patterns:
            return False
        return any(re.search(pattern, candidate, re.I) for pattern in patterns for candidate in self._url_match_candidates(url))

    def _dedupe_key(self, url: str, canonical: str) -> str:
        for raw in self.config.crawl.get("deduplicate_url_patterns", []):
            if isinstance(raw, dict):
                pattern = str(raw.get("pattern", ""))
                key = str(raw.get("key") or pattern)
            else:
                pattern = str(raw)
                key = pattern
            if not pattern:
                continue
            if any(re.search(pattern, candidate, re.I) for candidate in self._url_match_candidates(url, canonical)):
                return f"dedupe:{key}"
        return canonical

    def _execute_forms_enabled(self) -> bool:
        return bool(self.config.crawl.get("execute_forms", False))

    def _synthetic_text(self, name: str, page: str, prefix: str = "DRHL") -> str:
        digest = hashlib.sha256(f"{page}\0{name}".encode("utf-8")).hexdigest()[:8]
        return f"{prefix}_{digest}"

    def _database_forum_password_for_current_page(self) -> str | None:
        role_name = self._current_role.name if self._current_role else ""
        allowed_roles = self.config.crawl.get("forum_password_database_roles", [])
        if role_name not in {str(item) for item in allowed_roles}:
            return None
        current_url = str(self.driver.current_url or "") if self.driver is not None else ""
        fid = (parse_qs(urlsplit(current_url).query).get("fid") or [""])[0]
        if not fid.isdigit():
            return None
        database = self.config.database
        if str(database.get("driver", "")).lower() != "mysql":
            return None
        sql = f"SELECT password FROM mybb_forums WHERE fid={int(fid)} LIMIT 1"
        try:
            from ..database_probe import create_database_probe

            password = create_database_probe(database).scalar(sql).strip()
        except Exception:
            return None
        return password or None

    def _configured_form_value(self, name: str, key: str) -> str | None:
        role_name = self._current_role.name if self._current_role else ""
        if key == "pwverify":
            forum_password = self._database_forum_password_for_current_page()
            if forum_password is not None:
                return forum_password
        candidates = []
        values_by_role = self.config.crawl.get("form_values_by_role", {})
        if isinstance(values_by_role, dict):
            role_values = values_by_role.get(role_name, {})
            if isinstance(role_values, dict):
                candidates.append(role_values)
        global_values = self.config.crawl.get("form_values", {})
        if isinstance(global_values, dict):
            candidates.append(global_values)
        for values in candidates:
            for lookup in (name, key, name.casefold(), key.casefold()):
                if lookup in values:
                    return str(values[lookup])
        return None
    def _synthetic_form_value(
        self,
        name: str,
        field_type: str,
        current_value: str | None,
        page: str,
    ) -> str:
        value = current_value or ""
        if value:
            return value
        key = re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_")
        configured = self._configured_form_value(name, key)
        if configured is not None:
            return configured
        if "mail" in key:
            return f"drhl_{self._synthetic_text(name, page, '').strip('_').lower()}@example.test"
        if "password" in key or key in {"passwd", "pwd"}:
            return "12345678"
        if "phone" in key or "mobile" in key or "tel" in key:
            return "13800138000"
        if "date" in key:
            return "2026-01-01"
        if "time" in key:
            return "12:00"
        if "url" in key or "website" in key:
            return "http://example.test/"
        if field_type in {"number", "range"} or key.endswith("id") or key in {"id", "count", "num", "number"}:
            return "1"
        if "comment" in key or "message" in key or "content" in key or "description" in key:
            return self._synthetic_text(name, page, "comment")
        if "title" in key or "subject" in key or "name" in key or "first" in key or "last" in key:
            return self._synthetic_text(name, page, "text")
        if "affiliation" in key or "organization" in key or "company" in key:
            return self._synthetic_text(name, page, "org")
        return self._synthetic_text(name, page, "value")

    def _create_driver(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service

        progress("Starting Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        if self.config.crawl.get("headless", True):
            options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1440,1200")
        for argument in self.config.crawl.get("browser_arguments", []):
            options.add_argument(str(argument))
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver_path = self.config.crawl.get("driver_path")
        service = Service(executable_path=driver_path) if driver_path else Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(float(self.config.crawl.get("page_timeout", 20)))
        progress("Chrome WebDriver started")
        return driver

    def _login_steps(self, login: dict[str, Any]) -> list[dict[str, Any]]:
        steps = login.get("steps")
        if isinstance(steps, list):
            return [dict(step) for step in steps if isinstance(step, dict)]
        return [login]

    def _submit_post_login_step(self, action_url: str, data: dict[str, Any]) -> None:
        script = """
            const action = arguments[0];
            const data = arguments[1];
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = action;
            form.style.display = 'none';
            for (const [name, value] of Object.entries(data)) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = name;
                input.value = value == null ? '' : String(value);
                form.appendChild(input);
            }
            document.body.appendChild(form);
            HTMLFormElement.prototype.submit.call(form);
        """
        self.driver.execute_script(script, action_url, data)

    def _apply_browser_cookies(self, cookies: dict[str, str]) -> None:
        if not cookies:
            return
        base = self.config.target.base_url.rstrip("/") + "/"
        current = str(self.driver.current_url or "")
        if not current.startswith(base):
            self.driver.get(base)
        for name, value in cookies.items():
            try:
                self.driver.add_cookie({"name": str(name), "value": str(value), "path": "/"})
            except Exception as exc:
                progress(f"browser cookie skipped: {name}: {type(exc).__name__}")
    def _login_username(self, role: RoleConfig | None) -> str | None:
        if role is None or not role.crawl_login:
            return None
        for step in self._login_steps(role.crawl_login):
            data = dict(step.get("data", {}))
            for key in ("quick_username", "username", "email"):
                if data.get(key):
                    return str(data[key])
        return None

    def _database_mybb_post_key(self, role: RoleConfig | None) -> str | None:
        username = self._login_username(role)
        if not username:
            return None
        cache_key = (role.name if role else "", username)
        if cache_key in self._runtime_token_cache:
            return self._runtime_token_cache[cache_key]
        database = self.config.database
        if str(database.get("driver", "")).lower() != "mysql":
            return None
        escaped = username.replace("'", "''")
        sql = "SELECT MD5(CONCAT(loginkey,salt,regdate)) FROM mybb_users WHERE username='{}' LIMIT 1".format(escaped)
        try:
            from ..database_probe import create_database_probe

            token = create_database_probe(database).scalar(sql).strip()
        except Exception:
            return None
        if token:
            self._runtime_token_cache[cache_key] = token
            return token
        return None

    def _runtime_token(self, name: str) -> str | None:
        page = str(self.driver.page_source or "") if self.driver is not None else ""
        escaped = re.escape(name)
        patterns = [
            rf"[?&;]{escaped}=([^&\"'<>\s]+)",
            rf"name=[\"']{escaped}[\"'][^>]*value=[\"']([^\"']+)[\"']",
            rf"value=[\"']([^\"']+)[\"'][^>]*name=[\"']{escaped}[\"']",
            rf"\b{escaped}\s*=\s*[\"']([^\"']+)[\"']",
        ]
        for pattern in patterns:
            match = re.search(pattern, page, re.I)
            if match:
                return match.group(1).replace("&amp;", "&")
        if name == "my_post_key":
            return self._database_mybb_post_key(self._current_role)
        return None

    def _resolve_runtime_placeholders(self, value: str) -> str:
        resolved = str(value)
        for name in ("my_post_key", "post_key", "csrf", "token"):
            placeholder = "{" + name + "}"
            if placeholder in resolved:
                token = self._runtime_token(name)
                if token:
                    resolved = resolved.replace(placeholder, token)
        return resolved

    def _validate_login_step(self, role: RoleConfig, label: str, login: dict[str, Any]) -> None:
        expected_cookies = [str(item) for item in login.get("expect_cookies", [])]
        missing = [name for name in expected_cookies if self.driver.get_cookie(name) is None]
        if missing:
            raise RuntimeError(
                f"login step failed for role {role.name} ({label}); missing expected cookie(s): {', '.join(missing)}"
            )
        page_text = str(self.driver.page_source or "").casefold()
        for marker in login.get("forbid_text", []):
            value = str(marker).casefold()
            if value and value in page_text:
                raise RuntimeError(
                    f"login step failed for role {role.name} ({label}); forbidden login/denial text was still present"
                )
        required = [str(item).casefold() for item in login.get("require_text", []) if str(item)]
        missing_text = [item for item in required if item not in page_text]
        if missing_text:
            raise RuntimeError(
                f"login step failed for role {role.name} ({label}); required success text was not found"
            )
    def _login(self, role: RoleConfig) -> list[str]:
        if role.kind == "visitor" or not role.crawl_login:
            progress(f"Role {role.name} does not require login")
            return []
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as conditions
        from selenium.webdriver.support.ui import WebDriverWait

        extra_seed_urls: list[str] = []
        top_level_seed_urls = role.crawl_login.get("seed_urls", [])
        if isinstance(top_level_seed_urls, list):
            for seed in top_level_seed_urls:
                extra_seed_urls.append(absolute_url(self.config.target.base_url, str(seed)))

        steps = self._login_steps(role.crawl_login)
        for index, login in enumerate(steps, start=1):
            login_url = absolute_url(self.config.target.base_url, str(login.get("url", self.config.crawl.get("root_url", ""))))
            label = str(login.get("name") or f"step {index}/{len(steps)}")
            progress(f"Role {role.name} logging in ({label}): {login_url}")
            lingering_alert = self._dismiss_alert()
            if lingering_alert:
                progress(f"accepted lingering alert before login navigation: {self._short_text(lingering_alert)}")
            self.driver.get(login_url)
            wait = WebDriverWait(self.driver, float(login.get("timeout", 10)))
            method = str(login.get("method", "GET")).upper()
            data = dict(login.get("data", {}))
            if method == "POST" and data and not login.get("fields"):
                post_url = absolute_url(self.config.target.base_url, str(login.get("post_url", login.get("action", login.get("url", login_url)))))
                self._submit_post_login_step(post_url, data)
            else:
                for selector, value in login.get("fields", {}).items():
                    element = wait.until(conditions.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    element.clear()
                    element.send_keys(str(value))
                submit = login.get("submit")
                if submit:
                    wait.until(conditions.element_to_be_clickable((By.CSS_SELECTOR, submit))).click()
                else:
                    self.driver.find_element(By.CSS_SELECTOR, "form").submit()
            time.sleep(float(login.get("wait_after", 1)))
            self._validate_login_step(role, label, login)
            self._apply_browser_cookies(role.cookies)
            step_seed_urls = login.get("seed_urls", [])
            if isinstance(step_seed_urls, list):
                for seed in step_seed_urls:
                    extra_seed_urls.append(absolute_url(self.config.target.base_url, self._resolve_runtime_placeholders(str(seed))))
            progress(f"Role {role.name} login step completed ({label}); current page: {self.driver.current_url}")
        return list(dict.fromkeys(extra_seed_urls))

    def _network_requests(self, result: RoleCrawl, referer: str | None) -> None:
        preserve = list(self.config.crawl.get("preserve_query_parameters", []))
        drop = list(self.config.crawl.get("drop_query_parameters", []))
        path_patterns = list(self.config.crawl.get("path_parameter_patterns", []))
        scope_path = self.config.crawl.get("scope_path")
        for entry in self.driver.get_log("performance"):
            try:
                message = json.loads(entry["message"])["message"]
                if message["method"] != "Network.requestWillBeSent":
                    continue
                payload = message["params"]
                request = payload["request"]
                url = str(request["url"])
                if str(payload.get("type", "")) not in {"Document", "XHR", "Fetch", "Other"}:
                    continue
                if not in_scope(url, self.config.target.base_url, scope_path):
                    continue
                params = request_params(url, request.get("postData"))
                clean = {key: value for key, value in params.items() if self._should_record_parameter(key)}
                page = canonical_page(url, self.config.target.base_url, preserve, drop, path_patterns)
                method = str(request.get("method", "GET")).upper()
                current = result.requests.get(page)
                if current is None or (current.method == "GET" and method != "GET") or (not current.params and clean):
                    result.requests[page] = RequestSpec(method=method, params=clean, referer=referer)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue

    def _form_target(self, form: Any, current_url: str) -> tuple[str, str, str] | None:
        preserve = list(self.config.crawl.get("preserve_query_parameters", []))
        drop = list(self.config.crawl.get("drop_query_parameters", []))
        path_patterns = list(self.config.crawl.get("path_parameter_patterns", []))
        scope_path = self.config.crawl.get("scope_path")
        action = urljoin(current_url, form.get_attribute("action") or current_url)
        if not in_scope(action, self.config.target.base_url, scope_path):
            return None
        target = canonical_page(action, self.config.target.base_url, preserve, drop, path_patterns)
        method = (form.get_attribute("method") or "GET").upper()
        return action, target, method

    def _fallback_form_params_from_html(self, target: str, fill: bool = False) -> dict[str, str]:
        html_candidates: list[str] = []
        try:
            html_candidates.append(self.driver.page_source or "")
        except Exception:
            pass
        try:
            import requests

            response = requests.get(str(self.driver.current_url), timeout=10)
            if response.text:
                html_candidates.append(response.text)
        except Exception:
            pass

        target_name = target.split("?", 1)[0].rsplit("/", 1)[-1].casefold()
        field_pattern = re.compile(r"<(input|textarea|select)\b([^>]*)>(.*?</\1>)?", re.I | re.S)
        for html in html_candidates:
            if not html:
                continue
            form_blocks = re.findall(r"<form\b[^>]*>.*?</form>", html, re.I | re.S)
            selected = ""
            for block in form_blocks:
                action_match = re.search(r"\baction\s*=\s*['\"]?([^'\"\s>]*)", block, re.I)
                action = (action_match.group(1) if action_match else "").split("?", 1)[0].rsplit("/", 1)[-1].casefold()
                if not target_name or action == target_name:
                    selected = block
                    break
            if not selected:
                continue
            params: dict[str, str] = {}
            for match in field_pattern.finditer(selected):
                tag = match.group(1).lower()
                attrs = match.group(2) or ""
                tail = match.group(3) or ""
                name_match = re.search(r"\bname\s*=\s*['\"]?([^'\"\s>]*)", attrs, re.I)
                if not name_match:
                    continue
                name = name_match.group(1)
                field_type_match = re.search(r"\btype\s*=\s*['\"]?([^'\"\s>]*)", attrs, re.I)
                field_type = (field_type_match.group(1) if field_type_match else ("textarea" if tag == "textarea" else "text")).lower()
                if field_type in {"file", "button", "reset", "image"}:
                    continue
                value = ""
                if tag == "select":
                    selected_option = re.search(r"<option\b[^>]*\bselected\b[^>]*>(.*?)</option>", tail, re.I | re.S)
                    any_option = selected_option or re.search(r"<option\b([^>]*)>(.*?)</option>", tail, re.I | re.S)
                    if any_option:
                        attrs_or_text = any_option.group(1) if any_option.lastindex and any_option.lastindex >= 2 else ""
                        option_text = any_option.group(any_option.lastindex or 1)
                        value_match = re.search(r"\bvalue\s*=\s*['\"]?([^'\"\s>]*)", attrs_or_text, re.I)
                        value = value_match.group(1) if value_match else re.sub(r"<[^>]+>", "", option_text).strip()
                else:
                    value_match = re.search(r"\bvalue\s*=\s*['\"]([^'\"]*)['\"]", attrs, re.I)
                    if not value_match:
                        value_match = re.search(r"\bvalue\s*=\s*([^\s>]*)", attrs, re.I)
                    value = value_match.group(1) if value_match else ""
                value = self._synthetic_form_value(name, field_type, value, target)
                if self._should_record_parameter(name):
                    params[name] = value
            if params:
                return params
        return {}

    def _collect_form_params(self, form: Any, target: str, fill: bool = False) -> dict[str, str]:
        params: dict[str, str] = {}
        for field in form.find_elements("css selector", "input[name], textarea[name], select[name]"):
            name = field.get_attribute("name")
            field_type = (field.get_attribute("type") or "text").lower()
            if not name or field_type in {"file", "button"}:
                continue
            tag_name = field.tag_name.lower()
            if field_type in {"checkbox", "radio"}:
                if fill and not field.is_selected():
                    try:
                        field.click()
                    except Exception:
                        pass
                if not field.is_selected():
                    continue
                value = field.get_attribute("value") or "on"
            else:
                value = self._synthetic_form_value(
                    name,
                    field_type if tag_name != "textarea" else "textarea",
                    field.get_attribute("value"),
                    target,
                )
                if fill and field_type not in {"hidden", "submit", "image", "reset"} and tag_name != "select":
                    try:
                        field.clear()
                        field.send_keys(value)
                    except Exception:
                        pass
            if self._should_record_parameter(name):
                params[name] = value
        for key, value in list(params.items()):
            if not str(value):
                params[key] = self._synthetic_form_value(key, "text", "", target)
        fallback_params = self._fallback_form_params_from_html(target, fill=fill) if not params else {}
        if fallback_params:
            for key, value in fallback_params.items():
                if key not in params or not str(params[key]):
                    params[key] = value
        return params

    def _submit_form(self, form: Any) -> None:
        submitters = form.find_elements(
            "css selector",
            "input[type='submit'], button[type='submit'], button:not([type]), input[type='image']",
        )
        excluded_names = self._excluded_submit_names()
        excluded_value_markers = self._excluded_submit_value_markers()
        for submitter in submitters:
            try:
                name = str(submitter.get_attribute("name") or "").casefold()
                value = str(submitter.get_attribute("value") or submitter.text or "").casefold()
                if name and name in excluded_names:
                    continue
                if any(marker and marker in value for marker in excluded_value_markers):
                    continue
                if submitter.is_displayed() and submitter.is_enabled():
                    submitter.click()
                    return
            except Exception:
                continue
        form.submit()

    def _short_text(self, value: str, limit: int = 220) -> str:
        text = re.sub(r"\s+", " ", value).strip()
        return text[:limit] + ("..." if len(text) > limit else "")

    def _brief_exception(self, exc: Exception) -> str:
        text = str(exc).split("Stacktrace:", 1)[0]
        return self._short_text(text or type(exc).__name__)

    def _dismiss_alert(self) -> str | None:
        try:
            from selenium.common.exceptions import NoAlertPresentException

            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except NoAlertPresentException:
            return None
        except Exception:
            return None

    def _record_form(self, result: RoleCrawl, form: Any, current_url: str, current_page: str) -> None:
        descriptor = self._form_target(form, current_url)
        if descriptor is None:
            return
        _, target, method = descriptor
        params = self._collect_form_params(form, target, fill=False)
        result.nodes.append(target)
        result.edges.append({"from": current_page, "to": target})
        current = result.requests.get(target)
        if current is None or (current.method == "GET" and method != "GET") or (not current.params and params):
            result.requests[target] = RequestSpec(method=method, params=params, referer=current_page)

    def _execute_forms_on_page(self, result: RoleCrawl, current_url: str, current_page: str) -> list[str]:
        discovered_after_submit: list[str] = []
        if not self._execute_forms_enabled():
            return discovered_after_submit
        from selenium.webdriver.common.by import By

        preserve = list(self.config.crawl.get("preserve_query_parameters", []))
        drop = list(self.config.crawl.get("drop_query_parameters", []))
        path_patterns = list(self.config.crawl.get("path_parameter_patterns", []))
        excluded = [str(value).casefold() for value in self.config.crawl.get("exclude_url_markers", ["logout", "logoff"])]
        excluded.extend(str(value).casefold() for value in self.config.crawl.get("exclude_form_markers", []))
        limit = int(self.config.crawl.get("execute_forms_limit_per_page", 20))
        wait_after = float(self.config.crawl.get("execute_forms_wait_after", self.config.crawl.get("delay", 0.1)))
        forms = self.driver.find_elements(By.CSS_SELECTOR, "form")
        count = min(len(forms), max(0, limit))
        for index in range(count):
            try:
                lingering_alert = self._dismiss_alert()
                if lingering_alert:
                    progress(f"[{result.role}] accepted lingering alert before form navigation: {self._short_text(lingering_alert)}")
                self.driver.get(current_url)
                if wait_after:
                    time.sleep(wait_after)
                forms = self.driver.find_elements(By.CSS_SELECTOR, "form")
                if index >= len(forms):
                    break
                form = forms[index]
                descriptor = self._form_target(form, current_url)
                if descriptor is None:
                    continue
                action, target, method = descriptor
                form_context = " ".join([current_page, action, target]).casefold()
                excluded_marker = next((marker for marker in excluded if marker and marker in form_context), None)
                if excluded_marker:
                    progress(f"[{result.role}] skipping form execution on {current_page}; marker={excluded_marker}")
                    continue
                params = self._collect_form_params(form, target, fill=True)
                result.nodes.append(target)
                result.edges.append({"from": current_page, "to": target})
                result.requests[target] = RequestSpec(method=method, params=params, referer=current_page)
                progress(f"[{result.role}] executing form {index + 1}/{count}: {current_page} -> {target}")
                self._submit_form(form)
                if wait_after:
                    time.sleep(wait_after)
                alert_text = self._dismiss_alert()
                if alert_text:
                    progress(f"[{result.role}] accepted alert after form submission: {self._short_text(alert_text)}")
                self._network_requests(result, current_page)
                actual_url = self.driver.current_url
                if in_scope(actual_url, self.config.target.base_url, self.config.crawl.get("scope_path")):
                    actual_page = canonical_page(actual_url, self.config.target.base_url, preserve, drop, path_patterns)
                    if actual_page:
                        result.nodes.append(actual_page)
                        result.edges.append({"from": target, "to": actual_page})
                        discovered_after_submit.extend(self._extract_links_and_forms(result, actual_url, actual_page))
            except Exception as exc:
                alert_text = self._dismiss_alert()
                if alert_text:
                    progress(f"[{result.role}] accepted alert after form execution error: {self._short_text(alert_text)}")
                else:
                    progress(f"[{result.role}] form execution skipped after error: {type(exc).__name__}: {self._brief_exception(exc)}")
                continue
        return discovered_after_submit

    def _extract_links_and_forms(self, result: RoleCrawl, current_url: str, current_page: str) -> list[str]:
        from selenium.webdriver.common.by import By

        discovered: list[str] = []
        scope_path = self.config.crawl.get("scope_path")
        for element in self.driver.find_elements(By.CSS_SELECTOR, "a[href], frame[src], iframe[src]"):
            attribute = "href" if element.tag_name.lower() == "a" else "src"
            value = element.get_attribute(attribute)
            if not value:
                continue
            url = urljoin(current_url, value)
            if self._is_excluded_url(url):
                continue
            if in_scope(url, self.config.target.base_url, scope_path):
                discovered.append(url)

        for form in self.driver.find_elements(By.CSS_SELECTOR, "form"):
            self._record_form(result, form, current_url, current_page)
        return discovered

    def crawl(self, role: RoleConfig) -> RoleCrawl:
        self._current_role = role
        self.driver = self._create_driver()
        extra_seed_urls = self._login(role)
        base_url = self.config.target.base_url
        root_url = absolute_url(base_url, str(self.config.crawl.get("root_url", base_url)))
        preserve = list(self.config.crawl.get("preserve_query_parameters", []))
        drop = list(self.config.crawl.get("drop_query_parameters", []))
        path_patterns = list(self.config.crawl.get("path_parameter_patterns", []))
        strategy = str(self.config.crawl.get("strategy", "dfs")).lower()
        max_pages = int(self.config.crawl.get("max_pages", 500))
        delay = float(self.config.crawl.get("delay", 0.1))
        initial_urls = [*extra_seed_urls, root_url] if strategy == "bfs" else [root_url, *extra_seed_urls]
        queue = deque((url, None) for url in dict.fromkeys(initial_urls))
        visited: set[str] = set()
        result = RoleCrawl(role=role.name, kind=role.kind)
        checkpoint_interval = int(self.config.crawl.get("checkpoint_interval", 25))
        checkpoint_path = self.config.run_dir / "crawl" / f"{role.name}.partial.json"
        progress(f"Role {role.name} crawling from {root_url}; max pages {max_pages}")

        while queue and len(visited) < max_pages:
            url, parent = queue.pop() if strategy == "dfs" else queue.popleft()
            url = self._resolve_runtime_placeholders(url)
            if self._is_excluded_url(url):
                continue
            key = canonical_page(url, base_url, preserve, drop, path_patterns)
            visit_key = self._dedupe_key(url, key)
            if visit_key in visited:
                continue
            visited.add(visit_key)
            requested_page = key
            requested_params = {
                name: value
                for name, value in request_params(url).items()
                if self._should_record_parameter(name)
            }
            lingering_alert = self._dismiss_alert()
            if lingering_alert:
                progress(f"[{role.name}] accepted lingering alert before navigation: {self._short_text(lingering_alert)}")
            self.driver.get(url)
            if delay:
                time.sleep(delay)
            actual_url = self.driver.current_url
            actual_page = canonical_page(actual_url, base_url, preserve, drop, path_patterns)
            page = actual_page or requested_page
            progress(f"[{role.name}] page {len(visited)}/{max_pages}: {requested_page} (actual: {page}; queued {len(queue)})")
            result.nodes.append(requested_page)
            result.requests.setdefault(requested_page, RequestSpec(method="GET", params=requested_params, referer=parent))
            if parent is not None:
                result.edges.append({"from": parent, "to": requested_page})
            if page != requested_page:
                actual_params = {
                    name: value
                    for name, value in request_params(actual_url).items()
                    if self._should_record_parameter(name)
                }
                result.nodes.append(page)
                result.requests.setdefault(page, RequestSpec(method="GET", params=actual_params, referer=requested_page))
                result.edges.append({"from": requested_page, "to": page})
            self._network_requests(result, parent)
            discovered = self._extract_links_and_forms(result, actual_url, page)
            discovered.extend(self._execute_forms_on_page(result, actual_url, page))
            if checkpoint_interval > 0 and len(visited) % checkpoint_interval == 0:
                partial = RoleCrawl(role=result.role, kind=result.kind)
                partial.nodes = sorted(set(result.nodes))
                partial.edges = [
                    {"from": left, "to": right}
                    for left, right in sorted({(edge["from"], edge["to"]) for edge in result.edges})
                ]
                partial.requests = dict(result.requests)
                write_json(checkpoint_path, partial.to_dict())
                progress(f"[{role.name}] partial crawl checkpoint written: {checkpoint_path}")
            for item in discovered:
                item_key = canonical_page(item, base_url, preserve, drop, path_patterns)
                if self._dedupe_key(item, item_key) not in visited:
                    queue.append((item, page))

        result.nodes = sorted(set(result.nodes))
        unique_edges = {(edge["from"], edge["to"]) for edge in result.edges}
        result.edges = [{"from": left, "to": right} for left, right in sorted(unique_edges)]
        if checkpoint_interval > 0:
            write_json(checkpoint_path, result.to_dict())
        return result

    def close(self) -> None:
        if self.driver is not None:
            try:
                self.driver.quit()
            finally:
                self.driver = None























