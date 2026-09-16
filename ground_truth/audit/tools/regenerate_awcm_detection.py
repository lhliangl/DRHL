"""One-off regeneration of AWCM attack vectors + active detection.

Reuses the existing crawl artifacts and the fused HSNG in runs/awcm (no
re-crawl, no HSNG rebuild), regenerates attack vectors with the current
configs/awcm.json oracle (meta-refresh to index.php now counts as denial),
excludes m_cp_avatar.php?do= from the vectors, and re-runs active detection.
Only runs/awcm/analysis/{vectors,findings,vulnerability_report} are written;
other applications are untouched.
"""

from __future__ import annotations

import json
from pathlib import Path

import sys

ROOT = Path(r"D:\project\python\DRHL")
sys.path.insert(0, str(ROOT))

from drhl.config import load_config
from drhl.database import create_snapshot
from drhl.models import RoleCrawl
from drhl.graphs import build_dynamic_graph
from drhl.analysis import generate_vectors, ActiveDetector
from drhl.io import write_json
from drhl.reporting import write_vulnerability_report

RUN = ROOT / "runs" / "awcm"
EXCLUDED_PAGES = {"m_cp_avatar.php?do="}


def main() -> None:
    config = load_config(ROOT / "configs" / "awcm.json")

    # 1) Reuse crawl artifacts (no re-crawling).
    crawls = []
    for role in config.roles:
        artifact = RUN / "crawl" / f"{role.name}.json"
        crawl = RoleCrawl.from_dict(json.loads(artifact.read_text(encoding="utf-8")))
        crawls.append(crawl)
    print(f"loaded crawl artifacts: {[c.role for c in crawls]}")

    # 2) Reuse the fused HSNG (no rebuild); the dynamic graph is only
    #    re-derived from the same crawl artifacts for the access map.
    dynamic = build_dynamic_graph(crawls)
    fused = json.loads((RUN / "graphs" / "fused.json").read_text(encoding="utf-8"))
    fused["access"] = dynamic["access"]
    fused["nodes"] = sorted(set(dynamic["nodes"]) | set(fused["nodes"]))

    # 3) Regenerate attack vectors with the current config, excluding
    #    m_cp_avatar.php?do=.
    a = config.analysis
    vectors = generate_vectors(
        fused,
        [str(item) for item in a.get("identity_parameters", [])],
        [str(item) for item in a.get("static_exclude_patterns", [])],
        [str(item) for item in a.get("force_static_pages", [])],
        [str(item) for item in a.get("force_horizontal_pages", [])],
        [str(item) for item in a.get("horizontal_exclude_patterns", [])],
        [str(item) for item in a.get("vertical_only_patterns", [])],
        [str(item) for item in a.get("force_vertical_pages", [])],
        dict(a.get("vertical_overrides", {})),
        [str(item) for item in a.get("post_page_open_get_patterns", [])],
        [dict(item) for item in a.get("horizontal_page_overrides", [])],
        [str(item) for item in a.get("admin_only_exclude_patterns", [])],
        [str(item) for item in a.get("authenticated_only_exclude_patterns", [])],
    )
    before = len(vectors)
    vectors = [v for v in vectors if v.page not in EXCLUDED_PAGES]
    print(f"vectors: {before} -> {len(vectors)} (excluded {EXCLUDED_PAGES})")

    # 4) Re-run active detection (fresh snapshot only if no baseline exists).
    snapshot = create_snapshot(config.database, RUN / "database")
    if not (RUN / "database" / "baseline.sql").is_file():
        snapshot.create()
    detector = ActiveDetector(config, snapshot)
    findings = detector.run(vectors)

    # 5) Write the regenerated artifacts (awcm only).
    analysis_dir = RUN / "analysis"
    write_json(analysis_dir / "vectors.json", {"vectors": [v.to_dict() for v in vectors]})
    write_json(analysis_dir / "findings.json", {
        "summary": {
            "vulnerable": sum(1 for f in findings if f.status == "vulnerable"),
            "not_vulnerable": sum(1 for f in findings if f.status != "vulnerable"),
        },
        "findings": [f.to_dict() for f in findings],
    })
    write_vulnerability_report(findings, analysis_dir / "vulnerability_report.md")
    print("wrote runs/awcm/analysis/{vectors,findings,vulnerability_report}")
    vuln = [f for f in findings if f.status == "vulnerable"]
    print(f"vulnerable: {len(vuln)}")
    for f in vuln:
        print(f"  {f.category:20s} {f.page} | {f.actor} | {f.http_status}")


if __name__ == "__main__":
    main()
