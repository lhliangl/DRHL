"""Manual ground-truth verification for Jspblog (GT-032 .. GT-038).

None of the admin JSP pages consults the login session (the login page only
sets session attribute isLoggedIn, which no admin page reads). All seven
records use the visitor role as attacker.
"""

from __future__ import annotations

import json

import verifier as v

APP = "jspblog"


def _visitor_get_form(det, db, gt_id, page, markers) -> dict:
    del db
    r = v.Recorder(APP, gt_id)
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, page, {"method": "GET", "params": {}, "referer": None})
        exposed = all(marker in resp["body"] for marker in markers)
        body_file = r.save_body(f"{gt_id}_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET {page}",
            "status_code": resp["status_code"],
            "form_content_exposed": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET {page} returned {resp['status_code']} and serves the protected admin form "
               f"without any session (form_content_exposed={exposed}).")
    return r.finish(verdict, summary)


def gt032(det, db) -> dict:
    """admin/addnews.jsp — the add-news form is open to visitors."""
    return _visitor_get_form(det, db, "GT-032", "admin/addnews.jsp",
                             ["Add News", "addnews2.jsp", 'name="headline"'])


def gt033(det, db) -> dict:
    """admin/addnews2.jsp — visitor POST creates a news row (token row)."""
    r = v.Recorder(APP, "GT-033", db)
    tok = v.token("news")
    r.add("instrument", {"table": "news", "token_headline": tok})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/addnews2.jsp", {
            "method": "POST",
            "params": {"headline": tok, "body": "drhlgt body", "date": "x", "author": "x"},
            "referer": "admin/addnews.jsp",
        })
        created = bool(db.scalar(f"SELECT COUNT(*) FROM news WHERE headline='{tok}'"))
        body_file = r.save_body("gt033_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/addnews2.jsp headline={tok}",
            "status_code": resp["status_code"],
            "news_row_created": created,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST admin/addnews2.jsp returned {resp['status_code']}; a news row with the "
               f"token headline was created in the portal database (created={created}).")
    return r.finish(verdict, summary)


def gt034(det, db) -> dict:
    """admin/adduser.jsp — the user-creation form is open to visitors."""
    return _visitor_get_form(det, db, "GT-034", "admin/adduser.jsp",
                             ["Add Author", "adduser2.jsp", "name='name'"])


def gt035(det, db) -> dict:
    """admin/adduser2.jsp — visitor POST creates an application user (token row)."""
    r = v.Recorder(APP, "GT-035", db)
    tok = v.token("user")
    r.add("instrument", {"table": "user", "token_name": tok})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/adduser2.jsp", {
            "method": "POST",
            "params": {"name": tok, "author": "drhlgt@example.test", "submit": "Add"},
            "referer": "admin/adduser.jsp",
        })
        created = bool(db.scalar(f"SELECT COUNT(*) FROM user WHERE name='{tok}'"))
        body_file = r.save_body("gt035_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/adduser2.jsp name={tok}",
            "status_code": resp["status_code"],
            "user_row_created": created,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST admin/adduser2.jsp returned {resp['status_code']}; a user row with the "
               f"token name was created in the portal database (created={created}).")
    return r.finish(verdict, summary)


def gt036(det, db) -> dict:
    """admin/admin.jsp — the administration control-panel menu is open to visitors."""
    return _visitor_get_form(det, db, "GT-036", "admin/admin.jsp",
                             ["Control Panel", "addnews.jsp", "editnews.jsp"])


def gt037(det, db) -> dict:
    """admin/editnews.jsp — visitor opens the news-management page and sees
    the news content (token injected into a news body is exposed)."""
    r = v.Recorder(APP, "GT-037", db)
    tok = v.token("editlist")
    db.execute(f"UPDATE news SET body='{tok}' WHERE headline='Java'")
    r.add("instrument", {"table": "news", "row": "headline='Java'", "column": "body", "token": tok})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/editnews.jsp", {"method": "GET", "params": {}, "referer": None})
        exposed = tok in resp["body"]
        body_file = r.save_body("gt037_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET admin/editnews.jsp",
            "status_code": resp["status_code"],
            "news_content_token_exposed": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET admin/editnews.jsp returned {resp['status_code']}; the news-management page "
               f"lists the news rows and exposed the token injected into a news body (exposed={exposed}).")
    return r.finish(verdict, summary)


def gt038(det, db) -> dict:
    """admin/editnews2.jsp — visitor POST updates the news body (token1 -> token2)."""
    r = v.Recorder(APP, "GT-038", db)
    t1 = v.token("news_before")
    t2 = v.token("news_after")
    db.execute(f"UPDATE news SET body='{t1}' WHERE headline='Java'")
    r.add("instrument", {"table": "news", "row": "headline='Java'", "column": "body",
                         "token1": t1, "token2": t2})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/editnews2.jsp", {
            "method": "POST",
            "params": {"headline": "Java", "body": t2, "date": "x", "author": "x"},
            "referer": "admin/editnews.jsp",
        })
        after = db.scalar("SELECT body FROM news WHERE headline='Java' LIMIT 1")
        body_file = r.save_body("gt038_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/editnews2.jsp body={t2}",
            "status_code": resp["status_code"],
            "db_body_before": t1,
            "db_body_after": after,
            "updated": (after == t2),
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if after == t2 else "not_confirmed"
    summary = (f"visitor POST admin/editnews2.jsp returned {resp['status_code']}; the news body changed "
               f"{t1} -> {after} in the portal database (updated={after == t2}; the query carries no "
               f"WHERE clause, so it applies to every row).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt032, gt033, gt034, gt035, gt036, gt037, gt038):
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
        print(f"{item['gt_id']}: {item['verdict']} | restored={item.get('restore_verified')} | {item['summary'][:120]}")


if __name__ == "__main__":
    main()
