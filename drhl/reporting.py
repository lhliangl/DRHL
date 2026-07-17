from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from .models import Finding


CATEGORY_NAMES = {
    "admin_only": "垂直越权（管理员页面）",
    "authenticated_only": "未授权访问（登录用户页面）",
    "horizontal": "水平越权",
    "vertical": "垂直越权",
    "static_only": "静态发现的可直接访问页面",
}


def _grouped(items: list[Finding]):
    grouped = defaultdict(list)
    for item in items:
        grouped[(item.category, item.page)].append(item)
    return grouped


def write_vulnerability_report(findings: list[Finding], output: Path) -> None:
    vulnerable = [item for item in findings if item.status == "vulnerable"]
    not_vulnerable = [item for item in findings if item.status != "vulnerable"]
    lines = [
        "# DRHL 漏洞验证报告",
        "",
        f"- 已确认漏洞请求：{len(vulnerable)}",
        f"- 未发现漏洞请求：{len(not_vulnerable)}",
        "",
        "> 报告采用二分类口径：只有 confirmed vulnerable 会进入漏洞部分；证据不足、未配置安全探针、响应不匹配或请求错误均归入未发现漏洞。",
        "",
    ]

    def section(title: str, items: list[Finding]) -> None:
        lines.extend([f"## {title}", ""])
        if not items:
            lines.extend(["无。", ""])
            return
        for (category, page), page_findings in sorted(_grouped(items).items()):
            actors = ", ".join(dict.fromkeys(item.actor for item in page_findings))
            confidence = ", ".join(sorted(set(item.confidence for item in page_findings)))
            statuses = ", ".join(str(item.http_status) for item in page_findings)
            evidence = sorted({entry for item in page_findings for entry in item.evidence})
            errors = sorted({item.error for item in page_findings if item.error})
            lines.extend(
                [
                    f"### `{page}`",
                    "",
                    f"- 类型：{CATEGORY_NAMES.get(category, category)}",
                    f"- 测试角色：{actors}",
                    f"- HTTP 状态：{statuses}",
                    f"- 置信度：{confidence}",
                ]
            )
            for entry in evidence:
                lines.append(f"- 证据：{entry}")
            for error in errors:
                lines.append(f"- 验证错误：{error}")
            lines.append("")

    section("已确认漏洞", vulnerable)
    section("未发现漏洞", not_vulnerable)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def report_existing(findings_json: Path, output: Path) -> None:
    data = json.loads(findings_json.read_text(encoding="utf-8"))
    findings = [Finding(**item) for item in data.get("findings", [])]
    write_vulnerability_report(findings, output)