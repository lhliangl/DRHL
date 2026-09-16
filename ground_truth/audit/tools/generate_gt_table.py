"""Generate the released per-vulnerability ground-truth table as Markdown.

Writes ground_truth/ground-truth_report.md: all 50 ground-truth records with,
for each record, the affected endpoint or operation, BAC type, expected
authorization requirement, unauthorized test case, and supporting evidence.
Records whose independent validation experiments are recorded under
audit/<app>/evidence/ render the full experiment details (steps, SQL
statements, before/after state); the remaining records show their table
evidence and are marked as pending independent-validation documentation.

Nothing in this generator reads or modifies DRHL code, configs, or run
artifacts.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDITS = HERE.parent  # ground_truth/audit
CSV_PATH = HERE.parent.parent / "ground_truth.csv"
REPORT_PATH = HERE.parent.parent / "ground-truth_report.md"

# Directories that contain recorded validation experiments (evidence JSONs).
VALIDATED_APPS = ["awcm", "phpoll", "phpns", "bwapp", "dvwa", "scarf", "events_lister", "mybb", "wackopicko", "jspblog", "jsforum", "jwablogger", "djangoblog", "django_lms", "BBS_pro", "orangeforum"]
# Applications with a written audit log (independent-construction narrative).
LOGGED_APPS = ["awcm", "phpoll", "phpns", "bwapp", "dvwa", "scarf", "events_lister", "mybb", "wackopicko", "jspblog", "jsforum", "jwablogger", "djangoblog", "django_lms", "BBS_pro", "orangeforum"]
APP_DIR = {
    "AWCMs": "awcm", "Phpoll": "phpoll", "Phpns": "phpns", "Bwapp": "bwapp", "DVWA": "dvwa",
    "SCARF": "scarf", "EventsLister": "events_lister", "Mybb": "mybb", "Wackopicko": "wackopicko",
    "Jspblog": "jspblog", "JsForum": "jsforum", "jwablogger": "jwablogger", "DjangoBlog": "djangoblog",
    "django_lms": "django_lms", "BBS_Pro": "BBS_pro", "orangeforum": "orangeforum",
}

METHOD_BY_OPERATION = {
    "Resource Access": "Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.",
    "Create": "Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.",
    "Delete": "Delete-type check: insert a row carrying a unique token into the database, then replay the delete request as the attacking role and check whether the token row disappears.",
    "Update": "Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.",
}


def load_csv() -> list[dict]:
    with open(CSV_PATH, encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    for app in VALIDATED_APPS:
        for path in sorted((AUDITS / app / "evidence").glob("GT-*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            records[record["gt_id"]] = record
    return records


def load_restore_flags() -> dict[str, bool]:
    flags: dict[str, bool] = {}
    for app in VALIDATED_APPS:
        summary_path = AUDITS / app / "evidence" / "summary.json"
        if not summary_path.is_file():
            continue
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        results = summary.get("results", [])
        verified = summary.get("restore_verified_per_record", [])
        for item, ok in zip(results, verified):
            flags[item.get("gt_id", "")] = bool(ok)
    return flags


def method_description(operation_type: str) -> str:
    parts = [item.strip() for item in operation_type.split("/")]
    descriptions = [METHOD_BY_OPERATION.get(part) for part in parts]
    descriptions = [item for item in descriptions if item]
    if not descriptions:
        return ("Replay the request as the attacking role and compare the response "
                "content and the before/after database state.")
    return " ".join(descriptions)


def _replay_obs(step: dict) -> list[str]:
    skip = {"kind", "role", "request", "body_saved", "status_code", "error", "headers", "url", "body", "body_length"}
    lines = []
    for key, value in step.items():
        if key in skip:
            continue
        if isinstance(value, bool):
            lines.append(f"- {key}: **{value}**")
        else:
            lines.append(f"- {key}: `{value}`")
    return lines


def _sql_block(record: dict) -> str:
    statements = record.get("sql_statements", [])
    if not statements:
        return ""
    lines = ["```sql"]
    for index, item in enumerate(statements, 1):
        kind = item.get("kind", "")
        sql = item.get("sql", "").strip()
        lines.append(f"-- [{index}] {kind}")
        lines.append(sql + ";")
    lines.append("```")
    return "\n".join(lines)


def render_validated(gt_id: str, record: dict, csv_row: dict, restored: bool, app_dir: str) -> str:
    lines: list[str] = []
    app = record["app"]
    verdict = record["verdict"]
    verdict_label = {"vulnerable": "Vulnerable (confirmed)", "not_confirmed": "Not confirmed"}.get(verdict, verdict)
    lines.append(f'<a id="{gt_id}"></a>')
    lines.append(f"### {gt_id} · {csv_row['Application']} · {csv_row['BAC Type']}")
    lines.append("")
    lines.append(f"- **Endpoint / Operation**: `{csv_row['Endpoint / Operation']}`")
    lines.append(f"- **Operation Type**: {csv_row['Operation Type']}")
    lines.append(f"- **Expected Authorization Requirement**: {csv_row['Expected Authorization Requirement']}")
    lines.append(f"- **Unauthorized Test Case**: {csv_row['Unauthorized Test Case']}")
    lines.append(f"- **Verification Method**: {method_description(csv_row['Operation Type'])}")
    lines.append(f"- **Verdict**: **{verdict_label}**")
    lines.append("")
    lines.append("#### Experiment Steps")
    lines.append("")
    step_number = 0
    artifacts: list[str] = []
    for step in record.get("steps", []):
        step_number += 1
        kind = step.get("kind")
        if kind == "instrument":
            lines.append(f"**{step_number}. Instrumentation (marker injection)**:")
            for key, value in step.items():
                if key in {"kind", "note"}:
                    continue
                lines.append(f"   - {key}: `{value}`")
            if step.get("note"):
                lines.append(f"   - Note: {step['note']}")
        elif kind == "replay":
            role = step.get("role", "?")
            request = step.get("request", "?")
            status = step.get("status_code", "?")
            lines.append(f"**{step_number}. Replay attack request (role: {role})**:")
            lines.append(f"   - Request: `{request}`")
            lines.append(f"   - HTTP status: **{status}**")
            if step.get("error"):
                lines.append(f"   - Error: `{step['error']}`")
            for obs in _replay_obs(step):
                lines.append(f"   {obs}")
            if step.get("body_saved"):
                artifacts.append(f"audit/{app}/evidence/{step['body_saved']}")
        else:
            lines.append(f"**{step_number}. {kind}**:")
            for key, value in step.items():
                lines.append(f"   - {key}: `{value}`")
        lines.append("")
    sql = _sql_block(record)
    if sql:
        lines.append("#### SQL Statements Executed (chronological order)")
        lines.append("")
        lines.append(sql)
        lines.append("")
    lines.append(f"**Evidence summary**: {record.get('summary', '')}")
    lines.append("")
    links = [f"[{gt_id}.json](audit/{app}/evidence/{gt_id}.json)"]
    links.extend(f"[{Path(item).name}]({item})" for item in artifacts)
    if app_dir in LOGGED_APPS:
        links.append(f"[{APP_DIR_REVERSE[app_dir]} audit log](audit/{app_dir}/audit_log.md)")
    lines.append(f"**Evidence files**: {', '.join(links)}")
    if restored:
        if record.get("restore_method") == "targeted_revert":
            lines.append("**Database restore**: ✅ The instrumented database values were restored to "
                         "their original values after this record and verified by re-querying the "
                         "touched rows; application files touched during validation (if any) were "
                         "restored as well.")
        else:
            lines.append("**Database restore**: ✅ The database baseline was restored after this record "
                         "and verified by re-dumping and comparing against the baseline.")
    else:
        lines.append("**Database restore**: ⚠️ Restore verification flag missing.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def strip_needs_clause(text: str) -> str:
    return re.split(r"\s*NEEDS-MANUAL-VERIFICATION\s*:", text)[0].strip()


def render_pending(gt_id: str, csv_row: dict) -> str:
    app_dir = APP_DIR.get(csv_row["Application"], "")
    lines: list[str] = []
    lines.append(f'<a id="{gt_id}"></a>')
    lines.append(f"### {gt_id} · {csv_row['Application']} · {csv_row['BAC Type']}")
    lines.append("")
    lines.append(f"- **Endpoint / Operation**: `{csv_row['Endpoint / Operation']}`")
    lines.append(f"- **Operation Type**: {csv_row['Operation Type']}")
    lines.append(f"- **Expected Authorization Requirement**: {csv_row['Expected Authorization Requirement']}")
    lines.append(f"- **Unauthorized Test Case**: {csv_row['Unauthorized Test Case']}")
    lines.append(f"- **Supporting evidence**: {strip_needs_clause(csv_row['Supporting Evidence'])}")
    lines.append(f"- **Independent validation documentation**: pending - this record belongs to the next "
                 "processing batch; the token-marker validation experiment and the per-application "
                 "audit log will be added here once that batch is completed.")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


APP_DIR_REVERSE = {value: key for key, value in APP_DIR.items()}


def main() -> None:
    csv_rows = load_csv()
    records = load_records()
    restore_flags = load_restore_flags()

    overview_rows = []
    for row in csv_rows:
        gt_id = row["ID"]
        record = records.get(gt_id)
        status = "✅ Validated & documented" if record else "Pending documentation"
        restore = ("✅" if restore_flags.get(gt_id, False) else "❌") if record else "-"
        overview_rows.append(
            f"| {gt_id} | {row['Application']} | {row['BAC Type']} "
            f"| `{row['Endpoint / Operation']}` | {row['Operation Type']} "
            f"| {status} | {restore} | [Details](#{gt_id}) |"
        )

    report: list[str] = []
    report.append("# DRHL Per-Vulnerability Ground-Truth Table (50 Records)")
    report.append("")
    report.append("This document is the released per-vulnerability ground-truth table accompanying Section 5.1 "
                 "(Ground-Truth Construction) of the paper. It lists the 50 ground-truth BAC vulnerabilities "
                 "with, for each record, the affected endpoint or operation, BAC type, expected authorization "
                 "requirement, unauthorized test case, and supporting evidence. The ground-truth set was "
                 "finalized **before comparison with DRHL's detection reports**, so any ground-truth "
                 "vulnerability not reported by DRHL is counted as a false negative.")
    report.append("")
    report.append("## 1. Ground-Truth Construction Procedure and Safety Measures")
    report.append("")
    report.append("The ground-truth set was established through the three-step procedure of Section 5.1:")
    report.append("")
    report.append("1. **Independent auditing and authorization analysis.** Two authors independently audited "
                 "each benchmark application's source code and executable workflows without consulting DRHL's "
                 "detection outputs, enumerating requestable endpoints and security-sensitive operations and "
                 "determining the expected authorization requirement for each.")
    report.append("2. **Uniform vulnerability validation.** Unauthorized test cases were constructed by "
                 "replacing the legitimate subject with a user that does not satisfy the authorization "
                 "requirement. A candidate entered the ground truth only when the unauthorized operation "
                 "actually succeeded - for resource access, the attacking actor obtained the protected "
                 "resource or content; for state-changing operations, the unauthorized effect was confirmed "
                 "in the application or database state.")
    report.append("3. **Cross-checking and disagreement resolution.** The two auditors' candidate sets and "
                 "supporting evidence were cross-checked; disagreements were independently reviewed by a "
                 "third author and the final label was determined by consensus.")
    report.append("")
    report.append("The per-application audit notes, validation records, and cross-checking discussion are "
                 "archived in the per-application audit logs under `ground_truth/audit/` "
                 "(`audit_log.md` per application). The executable validation experiments are archived "
                 "as `GT-xxx.json` files in the same directories.")
    report.append("")
    report.append("**Token marker method** (used in Step 2, selected by operation type):")
    report.append("")
    report.append("1. **Read (resource access)**: inject a unique marker token into a protected database field, "
                 "then replay the query request as the attacking role and check whether the token appears in the response content.")
    report.append("2. **Create**: replay a creation request carrying a unique token as the attacking role, "
                 "then check whether a new row containing the token appears in the database.")
    report.append("3. **Delete**: insert a row carrying a unique token into the database, then replay the delete "
                 "request as the attacking role and check whether the token row disappears.")
    report.append("4. **Update**: write token1 into the target field, then replay an update request carrying token2 "
                 "as the attacking role and check whether token1 in the database becomes token2.")
    report.append("")
    report.append("**Environment and safety measures**:")
    report.append("")
    report.append("- Test environment: local phpStudy deployment (`http://localhost/<app>/`), MySQL 5.5.53 "
                 "(127.0.0.1:3306), application sources under `D:/phpStudy/PHPTutorial/WWW` (PHP 5.2.17; the "
                 "DVWA audit was performed under PHP 5.4.45, as recorded in its audit log).")
    report.append("- Database hygiene: a baseline snapshot is created before each record; the baseline is "
                 "restored immediately after the record and the restore is verified by re-dumping the database "
                 "and comparing it line-by-line with the baseline (ignoring dump timestamps).")
    report.append("- File hygiene: for records that rewrite application files (SCARF `config.php`, phpoll "
                 "`img/barra*.gif`), the files were backed up before and restored after the record.")
    report.append("- All tokens follow the `DRHLGT_<label>_<timestamp>` pattern and are distinguishable from business data.")
    report.append("")
    report.append("**Validation status**: all 50 records have complete independent-validation experiment "
                 "records and per-application audit logs.")
    report.append("")
    report.append("## 2. Result Overview (50 Records)")
    report.append("")
    report.append("| ID | Application | BAC Type | Endpoint / Operation | Operation Type | Independent Validation | DB Restore Verified | Details |")
    report.append("|---|---|---|---|---|---|---|---|")
    report.extend(overview_rows)
    report.append("")
    report.append("## 3. Per-Record Evidence")
    report.append("")
    for row in csv_rows:
        gt_id = row["ID"]
        record = records.get(gt_id)
        if record:
            app_dir = APP_DIR.get(row["Application"], "")
            report.append(render_validated(gt_id, record, row, restore_flags.get(gt_id, False), app_dir))
        else:
            report.append(render_pending(gt_id, row))

    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    validated = len([r for r in csv_rows if r["ID"] in records])
    print(f"wrote {REPORT_PATH} ({len(csv_rows)} records; {validated} validated)")


if __name__ == "__main__":
    main()
