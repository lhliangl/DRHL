from __future__ import annotations

from typing import Any

from ..models import RoleCrawl


def build_dynamic_graph(crawls: list[RoleCrawl]) -> dict[str, Any]:
    nodes: set[str] = set()
    edges: set[tuple[str, str]] = set()
    access: dict[str, dict[str, Any]] = {}

    for crawl in crawls:
        nodes.update(crawl.nodes)
        edges.update((edge["from"], edge["to"]) for edge in crawl.edges)
        for page in crawl.nodes:
            entry = access.setdefault(page, {"roles": [], "kinds": [], "requests": []})
            if crawl.role not in entry["roles"]:
                entry["roles"].append(crawl.role)
            if crawl.kind not in entry["kinds"]:
                entry["kinds"].append(crawl.kind)
            request = crawl.requests.get(page)
            if request is not None:
                entry["requests"].append(
                    {
                        "role": crawl.role,
                        "kind": crawl.kind,
                        "method": request.method,
                        "params": request.params,
                        "referer": request.referer,
                    }
                )

    for entry in access.values():
        entry["roles"].sort()
        entry["kinds"].sort()
    return {
        "nodes": sorted(nodes),
        "edges": [{"from": left, "to": right} for left, right in sorted(edges)],
        "access": dict(sorted(access.items())),
    }

