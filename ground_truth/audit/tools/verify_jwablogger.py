"""Manual ground-truth verification for jwablogger (GT-045).

The viewEntry handler serves the full content of a blog entry without
checking the is_visible flag. Because viewEntry responses are cached
(ehcache), the verification inserts a fresh non-visible entry (documented
precondition; first fetch is uncached) and checks that its token content is
served to a visitor. A naturally non-visible entry (1927) is also requested
as supporting evidence without any precondition.
"""

from __future__ import annotations

import json

import verifier as v

APP = "jwablogger"


def gt045(det, db) -> dict:
    r = v.Recorder(APP, "GT-045", db)
    tok = v.token("hidden_entry")
    next_id = db.scalar("SELECT COALESCE(MAX(blog_entry_id), 0) + 1 FROM blog_entry")
    db.execute(
        f"INSERT INTO blog_entry (author, title, tags, description, internal_name, external_url, "
        f"is_visible, has_comments, has_anonymous_comments) VALUES "
        f"('admin', '{tok}', 'drhlgt', '{tok} description', '{tok}_internal', '', "
        f"'false', 'false', 'false')"
    )
    db.execute(f"INSERT INTO blog_entry_text (blog_entry_id, blog_text) VALUES ({next_id}, '{tok} body text')")
    r.add("instrument", {
        "table": "blog_entry / blog_entry_text",
        "inserted_entry_id": next_id,
        "title_token": tok,
        "is_visible": "false",
        "note": "documented precondition: a fresh entry with is_visible='false' was inserted for the test "
                "(the released endpoint text names entry 5444/drhl_test_entry from the original deployment; "
                "in the current deployment that entry is a cached seeded row, so the fresh entry avoids the "
                "response cache); the database baseline was restored after the record",
    })
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, f"blogger/viewEntry/{next_id}/{tok}_internal.html", {
            "method": "GET", "params": {}, "referer": None,
        })
        exposed = tok in resp["body"]
        body_file = r.save_body("gt045_visitor_new_entry", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET blogger/viewEntry/{next_id}/{tok}_internal.html (is_visible='false')",
            "status_code": resp["status_code"],
            "non_visible_entry_token_exposed": exposed,
            "body_saved": body_file,
        })
        # Supporting evidence: a naturally non-visible entry (no precondition).
        natural = db.rows("SELECT blog_entry_id, title, internal_name FROM blog_entry "
                          "WHERE is_visible='false' AND blog_entry_id=1927 LIMIT 1")[0]
        resp2 = v.replay(det, sess, f"blogger/viewEntry/{natural[0]}/{natural[2]}.html", {
            "method": "GET", "params": {}, "referer": None,
        })
        natural_exposed = natural[1] in resp2["body"]
        body_file2 = r.save_body("gt045_visitor_1927", resp2["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET blogger/viewEntry/{natural[0]}/{natural[2]}.html "
                       f"(naturally non-visible entry, no precondition)",
            "status_code": resp2["status_code"],
            "natural_non_visible_entry_content_exposed": natural_exposed,
            "body_saved": body_file2,
        })
        # Negative control: entry writing requires login.
        neg = v.replay(det, sess, "blogger/saveEntry", {
            "method": "POST", "params": {"title": "x", "description": "x", "text": "x"},
            "referer": "blogger",
        })
        neg_denied = "Must be logged in" in neg["body"]
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "POST blogger/saveEntry (entry creation)",
            "status_code": neg["status_code"],
            "entry_creation_denied": neg_denied,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET blogger/viewEntry/{next_id} returned {resp['status_code']} and served the "
               f"full content of the fresh entry with is_visible='false' (token exposed={exposed}); a "
               f"naturally non-visible entry (1927) is likewise served (exposed={natural_exposed}), while "
               f"entry creation requires login (denied={neg_denied}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = [v.run_record(snap, lambda: gt045(det, db), baseline, cfg.database)]
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
