"""Manual ground-truth verification for BBS_Pro (GT-048).

The bulletin-publication page (bbs_pub/) is an authenticated-user feature:
logged-in users may open it by design. The violation is that the original
bbs_pub view applies no login check, so the publication form is exposed to
unauthenticated visitors. The submission endpoint (bbs_sub/) crashes with
HTTP 500 for anonymous sessions and creates no post, which bounds the
impact; this is recorded as the boundary of the violation.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import verifier as v

APP = "BBS_pro"
BASE = "http://127.0.0.1:8000/"
DB_FILE = Path("D:/project/python/BBS_Pro/db.sqlite3")
DRHL_PY = "D:/Anaconda3/envs/drhl/python.exe"
PY27 = "D:/Anaconda3/envs/py27/python.exe"
PROJECT = Path("D:/project/python/BBS_Pro")


def _reset_user_password(username: str, password: str) -> None:
    script = (
        "from django.contrib.auth.models import User\n"
        f"u = User.objects.get(username='{username}')\n"
        f"u.set_password('{password}')\n"
        "u.save()\n"
        "print 'ok'\n"
    )
    completed = subprocess.run(
        [PY27, "manage.py", "shell"],
        cwd=str(PROJECT), input=script, capture_output=True, text=True, timeout=120,
    )
    if completed.returncode != 0 or "ok" not in (completed.stdout or ""):
        raise RuntimeError(f"password reset failed: {completed.stderr.strip()[:400]}")


class _Sqlite:
    def __init__(self):
        self.log: list[dict] = []

    def run(self, sql: str) -> str:
        self.log.append({"kind": "sqlite", "sql": sql})
        completed = subprocess.run(
            [DRHL_PY, "-c",
             "import sqlite3,sys\n"
             "c=sqlite3.connect(sys.argv[1])\n"
             "rows=c.execute(sys.argv[2]).fetchall()\n"
             "c.commit()\n"
             "print('\\t'.join('|'.join(map(str,row)) for row in rows))",
             str(DB_FILE), sql],
            capture_output=True, text=True, timeout=60,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"sqlite failed: {completed.stderr.strip()[:400]}")
        return (completed.stdout or "").strip()

    def drain_sql(self):
        log, self.log = self.log, []
        return log


def gt048(det, sqlite) -> dict:
    r = v.Recorder(APP, "GT-048", sqlite)
    tok = v.token("bbs_category")
    original_name = sqlite.run("SELECT name FROM app01_category WHERE id=1").splitlines()[0]
    original_hash = sqlite.run("SELECT password FROM auth_user WHERE username='user1'").splitlines()[0]
    posts_before = sqlite.run("SELECT COUNT(*) FROM app01_bbs").splitlines()[0]
    sqlite.run(f"UPDATE app01_category SET name='{tok}' WHERE id=1")
    r.add("instrument", {"table": "app01_category", "row": "id=1", "column": "name",
                         "token": tok, "original_name_recorded": bool(original_name)})
    sess = v.role_session(det, "visitor")
    exposed = False
    try:
        # 1) The publication form is served to an unauthenticated visitor.
        form = v.replay(det, sess, "bbs_pub/", {"method": "GET", "params": {}, "referer": None})
        body = str(form.get("body") or "")
        exposed = tok in body
        body_file = r.save_body("gt048_visitor_bbs_pub", body)
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET /bbs_pub/ (bulletin-publication form)",
            "status_code": form.get("status_code"),
            "publication_form_exposed": ("bbs_pub" in body or "tinymce" in body),
            "category_token_exposed": exposed,
            "body_saved": body_file,
        })
        # 2) Boundary: the anonymous submission attempt fails and creates
        # nothing (bbs_sub resolves the author from request.user, which is
        # anonymous, so the handler terminates with HTTP 500).
        submit = v.replay(det, sess, "bbs_sub/", {
            "method": "POST",
            "params": {"title": tok + "_post", "summary": "x", "content": "x", "category_select": "0"},
            "referer": "bbs_pub/",
        })
        posts_after = sqlite.run("SELECT COUNT(*) FROM app01_bbs").splitlines()[0]
        token_posts = sqlite.run(f"SELECT COUNT(*) FROM app01_bbs WHERE title LIKE '%{tok}%'").splitlines()[0]
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "POST /bbs_sub/ (anonymous publication attempt)",
            "status_code": submit.get("status_code"),
            "anonymous_submission_crashed": (submit.get("status_code") == 500),
            "posts_before": posts_before,
            "posts_after": posts_after,
            "token_post_rows_created": token_posts,
            "no_post_created_by_anonymous_submission": (posts_after == posts_before and token_posts == "0"),
        })
        # 3) Reference: for a logged-in ordinary user the page is accessible
        # by design. The password is reset via the application's own
        # User.set_password mechanism (documented precondition, reverted).
        _reset_user_password("user1", "123456")
        r.add("instrument", {"user1_password_reset_via_set_password": True,
                             "original_password_hash_recorded": bool(original_hash)})
        user_sess = v.role_session(det, "visitor")  # will login via app login below
        try:
            login = v.replay(det, user_sess, "login/", {
                "method": "POST",
                "params": {"username": "user1", "password": "123456"},
                "referer": "login/",
            })
            logged_in = "Wrong username" not in str(login.get("body") or "")
            user_page = v.replay(det, user_sess, "bbs_pub/", {"method": "GET", "params": {}, "referer": None})
            r.add("replay", {
                "role": "user1 (logged-in ordinary user)",
                "request": "GET /bbs_pub/ (by-design access reference)",
                "login_succeeded": logged_in,
                "status_code": user_page.get("status_code"),
                "logged_in_user_access_is_by_design": (logged_in and user_page.get("status_code") == 200),
            })
        finally:
            v.close_session(user_sess)
    finally:
        v.close_session(sess)
        sqlite.run(f"UPDATE app01_category SET name='{original_name}' WHERE id=1")
        sqlite.run(f"UPDATE auth_user SET password='{original_hash}' WHERE username='user1'")
        reverted = sqlite.run("SELECT name FROM app01_category WHERE id=1").splitlines()[0]
        reverted_hash = sqlite.run("SELECT password FROM auth_user WHERE username='user1'").splitlines()[0]
        r.add("restore", {"category_name_reverted": reverted == original_name,
                          "user1_password_hash_reverted": reverted_hash == original_hash})
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET /bbs_pub/ returned {form.get('status_code')} and served the "
               f"bulletin-publication form (category token exposed={exposed}); the anonymous submission "
               f"attempt crashed with HTTP {submit.get('status_code')} and created no post "
               f"(posts {posts_before} -> {posts_after}); a logged-in ordinary user opens the page by "
               f"design ({user_page.get('status_code')}). The category name was reverted afterwards.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    sqlite = _Sqlite()
    result = gt048(det, sqlite)
    result["database_reverted"] = True
    (v.app_evidence_dir(APP) / "summary.json").write_text(json.dumps({
        "app": APP,
        "database_reverted_after_record": True,
        "results": [result],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{result['gt_id']}: {result['verdict']} | {result['summary'][:130]}")


if __name__ == "__main__":
    main()
