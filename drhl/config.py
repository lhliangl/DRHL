from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigError


def _resolve_secrets(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("env:"):
        variable = value[4:]
        if not variable:
            raise ConfigError("environment secret must use env:VARIABLE")
        if variable not in os.environ:
            raise ConfigError(f"required environment variable is not set: {variable}")
        return os.environ[variable]
    if isinstance(value, dict):
        return {key: _resolve_secrets(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_secrets(item) for item in value]
    return value


def _path(base: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


@dataclass(frozen=True)
class RoleConfig:
    name: str
    kind: str
    crawl_login: dict[str, Any] = field(default_factory=dict)
    http_login: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    artifact: Path | None = None


@dataclass(frozen=True)
class TargetConfig:
    base_url: str
    source_root: Path
    language: str
    public_extensions: tuple[str, ...]


@dataclass(frozen=True)
class PipelineConfig:
    path: Path
    run_dir: Path
    target: TargetConfig
    database: dict[str, Any]
    crawl: dict[str, Any]
    roles: tuple[RoleConfig, ...]
    analysis: dict[str, Any]
    repair: dict[str, Any]


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path).expanduser().resolve()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"configuration does not exist: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    data = _resolve_secrets(data)
    base = config_path.parent

    target_data = dict(data.get("target", {}))
    if not target_data.get("base_url") or not target_data.get("source_root"):
        raise ConfigError("target.base_url and target.source_root are required")
    language = str(target_data.get("language", "php")).lower()
    defaults = {
        "php": [".php"],
        "python": [".py"],
        "go": [".go"],
        "java": [".jsp"],
        "jsp": [".jsp"],
    }
    extensions = target_data.get("public_extensions", defaults.get(language, []))
    target = TargetConfig(
        base_url=str(target_data["base_url"]),
        source_root=_path(base, str(target_data["source_root"])),
        language=language,
        public_extensions=tuple(str(item).lower() for item in extensions),
    )
    assert target.source_root is not None

    crawl = dict(data.get("crawl", {}))
    roles = []
    seen = set()
    for raw in crawl.get("roles", []):
        name = str(raw.get("name", "")).strip()
        kind = str(raw.get("kind", "")).lower().strip()
        if not name or name in seen:
            raise ConfigError(f"role names must be unique and non-empty: {name!r}")
        if kind not in {"admin", "user", "visitor"}:
            raise ConfigError(f"role {name!r} has invalid kind {kind!r}")
        seen.add(name)
        roles.append(
            RoleConfig(
                name=name,
                kind=kind,
                crawl_login=dict(raw.get("crawl_login", {})),
                http_login=dict(raw.get("http_login", {})),
                headers={str(k): str(v) for k, v in raw.get("headers", {}).items()},
                cookies={str(k): str(v) for k, v in raw.get("cookies", {}).items()},
                artifact=_path(base, raw.get("artifact")),
            )
        )

    database = dict(data.get("database", {}))
    if database.get("driver") == "sqlite" and database.get("path"):
        database["path"] = str(_path(base, str(database["path"])))
    if crawl.get("driver_path"):
        crawl["driver_path"] = str(_path(base, str(crawl["driver_path"])))

    return PipelineConfig(
        path=config_path,
        run_dir=_path(base, str(data.get("run_dir", "runs/latest"))),
        target=target,
        database=database,
        crawl=crawl,
        roles=tuple(roles),
        analysis=dict(data.get("analysis", {})),
        repair=dict(data.get("repair", {})),
    )


def validate_config(config: PipelineConfig) -> None:
    if not config.target.source_root.is_dir():
        raise ConfigError(f"source root is not a directory: {config.target.source_root}")
    if not config.roles:
        raise ConfigError("crawl.roles must contain at least one role")
    mode = str(config.crawl.get("mode", "selenium")).lower()
    if mode not in {"selenium", "artifacts"}:
        raise ConfigError("crawl.mode must be selenium or artifacts")
    if mode == "artifacts":
        missing = [role.name for role in config.roles if not role.artifact or not role.artifact.is_file()]
        if missing:
            raise ConfigError(f"artifact mode is missing crawl files for roles: {', '.join(missing)}")
    detection_enabled = bool(config.analysis.get("active_detection", True))
    if (mode == "selenium" or detection_enabled) and config.database.get("driver", "none") == "none":
        raise ConfigError("database rollback is mandatory for Selenium crawling and active detection")

