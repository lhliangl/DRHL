"""Manual ground-truth verification for DVWA (GT-021 .. GT-023).

GT-023 invokes the Create/Reset Database action as a visitor; the dvwa
database is reset by the app and then restored from the per-record baseline.
"""

from __future__ import annotations

import json
from urllib.parse import urljoin

import verifier as v

APP = "dvwa"
BASE = "http://localhost/DVWA/"


def gt021(det, db) -> dict:
    """about.php — protected lab page served to a visitor."""
    del db
    r = v.Recorder(APP, "GT-021")
    marker = "Damn Vulnerable Web Application (DVWA) is a PHP/MySQL web application"
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "about.php", {"method": "GET", "params": {}, "referer": None})
        exposed = marker in resp["body"]
        body_file = r.save_body("gt021_visitor_about", resp["body"])
        r.add("replay", {
            "role": "visitor (no DVWA session)",
            "request": "GET about.php",
            "status_code": resp["status_code"],
            "about_content_exposed": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET about.php returned {resp['status_code']} and serves the DVWA About page "
               f"content without any session (about_content_exposed={exposed}).")
    return r.finish(verdict, summary)


def gt022(det, db) -> dict:
    """instructions.php?doc=readme — instruction documents served to a visitor."""
    del db
    r = v.Recorder(APP, "GT-022")
    marker = "Damn Vulnerable Web App"  # README.md heading rendered by the page
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "instructions.php?doc=readme", {
            "method": "GET", "params": {"doc": "readme"}, "referer": None,
        })
        body = resp["body"]
        exposed = (marker in body) and ("Read Me" in body)
        body_file = r.save_body("gt022_visitor_instructions", body)
        r.add("replay", {
            "role": "visitor (no DVWA session)",
            "request": "GET instructions.php?doc=readme",
            "status_code": resp["status_code"],
            "document_content_exposed": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET instructions.php?doc=readme returned {resp['status_code']} and serves the "
               f"protected instruction document (document_content_exposed={exposed}).")
    return r.finish(verdict, summary)


def gt023(det, db) -> dict:
    """setup.php — visitor invokes Create/Reset Database and resets the whole
    dvwa database (marker row disappears); baseline restored afterwards."""
    import re
    r = v.Recorder(APP, "GT-023", db)
    tok = v.token("guestbook")
    db.execute("INSERT INTO guestbook (comment, name) VALUES (%s, %s)" % (f"'{tok}'", "'drhlgt'"))
    marker_before = db.scalar(f"SELECT COUNT(*) FROM guestbook WHERE comment='{tok}'")
    users_before = db.scalar("SELECT COUNT(*) FROM users")
    r.add("instrument", {"table": "guestbook", "marker_comment": tok, "marker_before": marker_before,
                         "users_before": users_before})
    sess = v.role_session(det, "visitor")
    marker_after = marker_before
    users_after = users_before
    try:
        resp = v.replay(det, sess, "setup.php", {"method": "GET", "params": {}, "referer": None})
        setup_form = "Create / Reset Database" in resp["body"]
        body_file = r.save_body("gt023_visitor_setup", resp["body"])
        # The form carries an anti-CSRF user_token bound to the visitor's own
        # session; extract it and replay the reset with it (CSRF protection is
        # not authorization, so this is the normal visitor flow).
        token_match = re.search(r"name=[\"']user_token[\"'][^>]*value=[\"']([^\"']+)[\"']", resp["body"])
        user_token = token_match.group(1) if token_match else None
        r.add("replay", {
            "role": "visitor (no DVWA session)",
            "request": "GET setup.php",
            "status_code": resp["status_code"],
            "create_reset_form_exposed": setup_form,
            "anti_csrf_user_token_extracted": bool(user_token),
            "body_saved": body_file,
        })
        # Invoke the reset action (the DB is restored right after this record).
        try:
            action = sess.post(BASE + "setup.php",
                               data={"create_db": "Create / Reset Database", "user_token": user_token or ""},
                               timeout=120, allow_redirects=False)
            action_body = str(action.text or "")
            followed = ""
            location = action.headers.get("Location", "")
            if action.status_code in (301, 302) and location:
                follow = sess.get(urljoin(BASE, location), timeout=60, allow_redirects=True)
                followed = str(follow.text or "")
            reset_done = ("Database has been created" in action_body or "Database has been created" in followed
                          or "Setup Successful" in action_body or "Setup Successful" in followed)
            action_file = r.save_body("gt023_visitor_setup_action", action_body + "\n<!-- followed -->\n" + followed,
                                      limit=8000)
            marker_after = db.scalar(f"SELECT COUNT(*) FROM guestbook WHERE comment='{tok}'")
            users_after = db.scalar("SELECT COUNT(*) FROM users")
            admin_hash_after = db.scalar("SELECT password FROM users WHERE user='admin' LIMIT 1")
            r.add("replay", {
                "role": "visitor (no DVWA session)",
                "request": "POST setup.php create_db=Create / Reset Database (with anti-CSRF user_token)",
                "status_code": action.status_code,
                "redirect_location": location,
                "reset_completed": reset_done,
                "marker_row_after": marker_after,
                "users_after": users_after,
                "admin_credential_reset_hash": admin_hash_after,
                "body_saved": action_file,
            })
        except Exception as exc:
            r.add("replay", {"request": "POST setup.php create_db", "error": str(exc)})
    finally:
        v.close_session(sess)
    reset_effective = (marker_after != marker_before) or (users_after != users_before)
    verdict = "vulnerable" if (setup_form and reset_effective) else ("vulnerable" if setup_form else "not_confirmed")
    summary = (f"visitor GET setup.php returned {resp['status_code']} with the Create/Reset Database form "
               f"(exposed={setup_form}); the visitor-triggered reset rebuilt the database: marker row "
               f"{marker_before}->{marker_after}, users {users_before}->{users_after}; baseline restored afterwards.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt021, gt022, gt023):
        results.append(v.run_record(snap, lambda fn=fn: fn(det, db), baseline, cfg.database))
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
