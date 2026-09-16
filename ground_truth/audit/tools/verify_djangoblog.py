"""Manual ground-truth verification for DjangoBlog (GT-046).

PostDetail renders any post selected by slug regardless of its status. The
verification inserts a fresh unpublished post (status=0) whose title and
content carry marker tokens, requests it as a visitor, and checks that the
tokens appear in the served page. The inserted post is deleted afterwards
(targeted revert, verified by re-querying).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import verifier as v

APP = "djangoblog"
BASE = "http://localhost:8000/"
DB_FILE = Path("D:/project/python/DjangoBlog/db.sqlite3")
DRHL_PY = "D:/Anaconda3/envs/drhl/python.exe"


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


def gt046(det, sqlite) -> dict:
    r = v.Recorder(APP, "GT-046", sqlite)
    tok = v.token("unpublished")
    slug = tok.lower()
    # Insert a fresh unpublished post (status=0) with marker tokens.
    sqlite.run(
        f"INSERT INTO blog_post (title, slug, author_id, content, created_on, updated_on, status) "
        f"VALUES ('{tok}', '{slug}', 1, '{tok} content', datetime('now'), datetime('now'), 0)"
    )
    r.add("instrument", {"table": "blog_post", "inserted_unpublished_post": {"title": tok, "slug": slug,
                         "status": 0, "content_token": tok + " content"}})
    sess = v.role_session(det, "visitor")
    exposed = False
    try:
        raw = v.replay(det, sess, f"{slug}/", {"method": "GET", "params": {}, "referer": None})
        body = str(raw.get("body") or "")
        exposed = tok in body
        body_file = r.save_body("gt046_visitor_unpublished", body)
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET /{slug}/ (unpublished post, status=0)",
            "status_code": raw.get("status_code"),
            "unpublished_post_token_exposed": exposed,
            "body_saved": body_file,
        })
    finally:
        v.close_session(sess)
        sqlite.run(f"DELETE FROM blog_post WHERE slug='{slug}'")
        remaining = sqlite.run(f"SELECT COUNT(*) FROM blog_post WHERE slug='{slug}'")
        r.add("restore", {"inserted_post_deleted": remaining == "0"})
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"a fresh unpublished post (status=0) with marker tokens was inserted; visitor GET "
               f"/{slug}/ returned {raw.get('status_code')} and served the unpublished post content "
               f"(token exposed={exposed}); the inserted post was deleted afterwards.")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    sqlite = _Sqlite()
    result = gt046(det, sqlite)
    result["restore_method"] = "targeted_revert"
    result["restore_verified"] = all(
        bool(value) for step in result.get("steps", [])
        if step.get("kind") == "restore"
        for key, value in step.items() if key != "kind" and isinstance(value, bool)
    )
    (v.app_evidence_dir(APP) / "summary.json").write_text(json.dumps({
        "app": APP,
        "restore_verified_per_record": [result["restore_verified"]],
        "restore_note": ("targeted revert: the inserted post was deleted and verified by re-querying "
                         "(no full baseline restore was needed)"),
        "results": [result],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{result['gt_id']}: {result['verdict']} | {result['summary'][:130]}")


if __name__ == "__main__":
    main()
