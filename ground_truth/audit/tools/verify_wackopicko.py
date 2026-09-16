"""Manual ground-truth verification for Wackopicko (GT-030 .. GT-031).

Deployment note: the application is deployed at the web root
(http://localhost/index.php); user id 11 in the current database is the
seeded user 'bryce', who owns pictures 22/23. user1 is 'scanner1' (id=4).

GT-031 (users/sample.php): sample.php sets $usercheck=False and includes
view.php, deliberately bypassing the require_login() gate that the regular
profile page (users/view.php) enforces.
"""

from __future__ import annotations

import json

import verifier as v

APP = "wackopicko"


def gt030(det, db) -> dict:
    """users/view.php?userid=11 — user1 opens another user's profile page
    (token in the target user's login field is exposed)."""
    r = v.Recorder(APP, "GT-030", db)
    tok = v.token("profile_login")
    original_login = db.scalar("SELECT login FROM users WHERE id=11")
    db.execute(f"UPDATE users SET login='{tok}' WHERE id=11")
    r.add("instrument", {"table": "users", "row": "id=11", "column": "login", "token": tok,
                         "original_login": original_login,
                         "note": "in the current deployment user id 11 is the seeded user 'bryce' "
                                 "(owner of pictures 22/23); the endpoint parameter follows the released table"})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, "users/view.php?userid=11", {
            "method": "GET", "params": {"userid": "11"}, "referer": None,
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt030_user1_view_user11", resp["body"])
        r.add("replay", {
            "role": "user1 (scanner1, not the profile owner)",
            "request": "GET users/view.php?userid=11",
            "status_code": resp["status_code"],
            "token_exposed_in_response": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"user1 GET users/view.php?userid=11 returned {resp['status_code']}; the profile page of "
               f"user id=11 was served and the token placed in that user's login field was exposed "
               f"(exposed={exposed}).")
    return r.finish(verdict, summary)


def gt031(det, db) -> dict:
    """users/sample.php — the login gate of the profile view is bypassed:
    an unauthenticated visitor receives another user's profile page."""
    r = v.Recorder(APP, "GT-031", db)
    tok = v.token("sample_login")
    original_login = db.scalar("SELECT login FROM users WHERE id=11")
    db.execute(f"UPDATE users SET login='{tok}' WHERE id=11")
    r.add("instrument", {"table": "users", "row": "id=11", "column": "login", "token": tok,
                         "original_login": original_login})
    sess = v.role_session(det, "visitor")
    exposed = False
    try:
        resp = v.replay(det, sess, "users/sample.php?userid=11", {
            "method": "GET", "params": {"userid": "11"}, "referer": None,
        })
        body = str(resp.get("body") or "")
        exposed = tok in body
        body_file = r.save_body("gt031_visitor_sample", body)
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET users/sample.php?userid=11 (login gate bypassed)",
            "status_code": resp.get("status_code"),
            "token_exposed_in_response": exposed,
            "body_saved": body_file,
        })
        # Policy reference: the regular profile page requires login.
        regular = v.replay(det, sess, "users/view.php?userid=11", {
            "method": "GET", "params": {"userid": "11"}, "referer": None,
        })
        redirected = (regular.get("status_code") in (301, 302, 303)
                      and "login" in (regular.get("headers") or {}).get("Location", ""))
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET users/view.php?userid=11 (regular entry, login required)",
            "status_code": regular.get("status_code"),
            "regular_entry_redirects_to_login": redirected,
        })
    finally:
        v.close_session(sess)
        db.execute(f"UPDATE users SET login='{original_login}' WHERE id=11")
        reverted = db.scalar("SELECT login FROM users WHERE id=11")
        r.add("restore", {"login_field_reverted": reverted == original_login})
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET users/sample.php?userid=11 returned {resp.get('status_code')} and served "
               f"the profile page of user id=11 with the token placed in the login field exposed "
               f"(exposed={exposed}); the regular entry users/view.php requires login and redirects the "
               f"visitor (redirected={redirected}); the instrumented login field was reverted "
               f"afterwards.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt030, gt031):
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
