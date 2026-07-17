from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


def _base_page(page: str) -> str:
    return PurePosixPath(str(page).split("?", 1)[0].lstrip("/")).as_posix()


def fuse_graphs(dynamic: dict[str, Any], static: dict[str, Any]) -> dict[str, Any]:
    dynamic_nodes = set(dynamic.get("nodes", []))
    observed_base_pages = {_base_page(page) for page in dynamic_nodes}
    static_pages = set(static.get("url_to_source", {}))
    classifications = dict(static.get("classifications", {}))

    up_prime0 = set(classifications.get("UP_prime0", [])) or {
        page for page in static_pages if _base_page(page) in observed_base_pages
    }
    updiff1 = set(classifications.get("UPdiff1", []))
    updiff2 = set(classifications.get("UPdiff2", []))
    if not (updiff1 or updiff2):
        updiff2 = static_pages - up_prime0
    updiff = set(classifications.get("UPdiff", [])) or (updiff1 | updiff2)
    cp_nodes = set(classifications.get("CP", []))

    static_only = sorted(updiff)
    # New detection policy: anonymous/static-only probing is limited to isolated
    # static UP nodes (UPdiff2) and component pages (CP).  UPdiff1 remains in
    # HSNG but is not forced with a visitor by the static-only vector generator.
    static_detection_pages = sorted(updiff2 | cp_nodes)

    all_nodes = dynamic_nodes | static_pages | cp_nodes
    origins = {}
    for node in sorted(all_nodes):
        sources = []
        if node in dynamic_nodes:
            sources.append("dynamic")
        if node in static_pages or node in cp_nodes:
            sources.append("static")
        origins[node] = sources

    source_map = dict(static.get("url_to_source", {}))
    for cp in cp_nodes:
        source_map.setdefault(cp, cp)

    return {
        "nodes": sorted(all_nodes),
        # Browser navigation and request relationships only.
        "edges": dynamic.get("edges", []),
        # Source include/import/request relationships are kept separate from navigation.
        "static_edges": static.get("edges", []),
        "node_origins": origins,
        "access": dynamic.get("access", {}),
        "static_only": static_only,
        "static_detection_pages": static_detection_pages,
        "source_map": source_map,
        "static_classifications": {
            **classifications,
            "UP_prime0": sorted(up_prime0),
            "UPdiff1": sorted(updiff1),
            "UPdiff2": sorted(updiff2),
            "UPdiff": sorted(updiff),
            "CP": sorted(cp_nodes),
        },
    }
