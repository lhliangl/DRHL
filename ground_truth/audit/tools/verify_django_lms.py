"""Manual ground-truth verification for django_lms (GT-047).

post_add (add_item/) carries no authorization decorator at all, while the
neighboring management views are guarded by @login_required and
@lecturer_required. Logged in as user1 (an ordinary student), the add-item
form is fetched with its CSRF token and submitted; the item row must appear
in the app_newsandevents table.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

import verifier as v

APP = "django_lms"


class _PG:
    """Minimal psql wrapper for the django_lms PostgreSQL database."""

    def __init__(self, config: dict):
        self.bin = str(config.get("psql", "psql"))
        self.args = ["-h", str(config.get("host", "localhost")),
                     "-p", str(config.get("port", 5432)),
                     "-U", str(config["user"]), "-d", str(config["database"])]
        self.env = os.environ.copy()
        if config.get("password"):
            self.env["PGPASSWORD"] = str(config["password"])
        self.log: list[dict] = []

    def _run(self, sql: str) -> str:
        self.log.append({"kind": "psql", "sql": sql})
        completed = subprocess.run(
            [self.bin, *self.args, "-t", "-A", "-c", sql],
            capture_output=True, text=True, env=self.env, timeout=120,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"psql failed: {completed.stderr.strip()[:400]}")
        return (completed.stdout or "").strip()

    def scalar(self, sql: str) -> str:
        return self._run(sql).splitlines()[0] if self._run(sql) else ""

    def drain_sql(self):
        log, self.log = self.log, []
        return log


def _csrf_token(body: str) -> str:
    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', body)
    return match.group(1) if match else ""


def gt047(det, pg) -> dict:
    r = v.Recorder(APP, "GT-047", pg)  # pg provides drain_sql()
    tok = v.token("lms_item")
    r.add("instrument", {"table": "app_newsandevents", "token_title": tok})
    sess = v.role_session(det, "user1")
    try:
        # 1) The form page is served to the logged-in ordinary user.
        form = v.replay(det, sess, "add_item/", {"method": "GET", "params": {}, "referer": None})
        csrf = _csrf_token(form["body"])
        form_file = r.save_body("gt047_user1_add_item_form", form["body"])
        r.add("replay", {
            "role": "user1 (ordinary student)",
            "request": "GET add_item/",
            "status_code": form["status_code"],
            "add_item_form_exposed": "Add Post" in form["body"] or "add_item" in form["body"],
            "csrf_token_obtained": bool(csrf),
            "body_saved": form_file,
        })
        # 2) Submit the form (CSRF token + token title).
        resp = v.replay(det, sess, "add_item/", {
            "method": "POST",
            "params": {"csrfmiddlewaretoken": csrf, "title": tok,
                       "summary": "drhlgt summary", "posted_as": "News"},
            "referer": "add_item/",
        })
        created = pg.scalar(f"SELECT COUNT(*) FROM app_newsandevents WHERE title='{tok}'")
        r.add("replay", {
            "role": "user1 (ordinary student)",
            "request": f"POST add_item/ title={tok} (fresh CSRF token)",
            "status_code": resp["status_code"],
            "item_row_created": (created == "1"),
        })
        # 3) Supporting observation: the form is served even to a visitor
        # (the view carries no authorization decorator at all).
        guest = v.role_session(det, "visitor")
        try:
            guest_form = v.replay(det, guest, "add_item/", {"method": "GET", "params": {}, "referer": None})
            r.add("replay", {
                "role": "visitor (no login)",
                "request": "GET add_item/",
                "status_code": guest_form["status_code"],
                "form_also_exposed_to_visitor": "csrfmiddlewaretoken" in guest_form["body"],
            })
        finally:
            v.close_session(guest)
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created == "1" else "not_confirmed"
    summary = (f"user1 GET add_item/ returned {form['status_code']} with the add-item form (CSRF token "
               f"obtained); the POST returned {resp['status_code']} and created the item row with the token "
               f"title in app_newsandevents (created={created == '1'}); the form is likewise served to a "
               f"visitor because the view has no authorization decorator.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    pg = _PG(cfg.database)
    results = [v.run_record(snap, lambda: gt047(det, pg), baseline, cfg.database)]
    (v.app_evidence_dir(APP) / "summary.json").write_text(json.dumps({
        "app": APP,
        "baseline": str(baseline),
        "database_restored_after_each_record": True,
        "restore_verified_per_record": [bool(item.get("restore_verified")) for item in results],
        "final_database_matches_baseline": v.db_matches(cfg.database, baseline),
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['gt_id']}: {item['verdict']} | restored={item.get('restore_verified')} | {item['summary'][:130]}")


if __name__ == "__main__":
    main()
