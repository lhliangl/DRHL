from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RequestSpec:
    method: str = "GET"
    params: dict[str, Any] = field(default_factory=dict)
    referer: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RequestSpec":
        return cls(
            method=str(value.get("method", "GET")).upper(),
            params=dict(value.get("params", {})),
            referer=value.get("referer"),
        )


@dataclass
class RoleCrawl:
    role: str
    kind: str
    nodes: list[str] = field(default_factory=list)
    edges: list[dict[str, str]] = field(default_factory=list)
    requests: dict[str, RequestSpec] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "kind": self.kind,
            "nodes": sorted(set(self.nodes)),
            "edges": self.edges,
            "requests": {page: asdict(spec) for page, spec in self.requests.items()},
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RoleCrawl":
        return cls(
            role=str(value["role"]),
            kind=str(value["kind"]),
            nodes=list(value.get("nodes", [])),
            edges=list(value.get("edges", [])),
            requests={page: RequestSpec.from_dict(spec) for page, spec in value.get("requests", {}).items()},
        )


@dataclass
class AttackVector:
    category: str
    page: str
    authorized_roles: list[str]
    request: RequestSpec
    identity_parameters: list[str] = field(default_factory=list)
    page_overrides: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        return result


@dataclass
class Finding:
    category: str
    page: str
    actor: str
    status: str
    confidence: str
    method: str
    http_status: int | None
    evidence: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
