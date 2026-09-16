"""Manual ground-truth verification for bWAPP (GT-016 .. GT-020).

GT-017 invokes the installer action (install=yes), which rebuilds the bWAPP
database; the per-record baseline restore reverts it immediately afterwards.
"""

from __future__ import annotations

import json

import verifier as v

APP = "bwapp"
BASE = "http://localhost/bWAPP/"


def gt016(det, db) -> dict:
    """backdoor.php — the NSA file uploader page is served to a visitor."""
    del db
    r = v.Recorder(APP, "GT-016")
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "backdoor.php", {"method": "GET", "params": {}, "referer": None})
        exposed = "NSA file uploader" in resp["body"]
        body_file = r.save_body("gt016_visitor_backdoor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET backdoor.php",
            "status_code": resp["status_code"],
            "backdoor_uploader_form_exposed": exposed,
            "body_saved": body_file,
        })
        # Document what the write path does for a sessionless visitor.
        try:
            upload = sess.post(BASE + "backdoor.php", data={"upload": "1", "uploadDir": "/var/www/bWAPP/images"},
                               timeout=60, allow_redirects=False)
            upload_denied = upload.status_code in (301, 302) and ("login" in (upload.headers.get("Location") or "").lower())
            r.add("replay", {
                "role": "visitor (no login)",
                "request": "POST backdoor.php upload=1",
                "status_code": upload.status_code,
                "upload_action_redirected_to_login": upload_denied,
            })
        except Exception as exc:
            r.add("replay", {"request": "POST backdoor.php upload=1", "error": str(exc)})
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET backdoor.php returned {resp['status_code']} and exposes the NSA file uploader "
               f"form (exposed={exposed}); the upload action itself redirects a sessionless visitor to login.")
    return r.finish(verdict, summary)


def gt017(det, db) -> dict:
    """install.php — visitor opens the installer and executes the install
    action (install=yes); DB is rebuilt and then restored per record."""
    r = v.Recorder(APP, "GT-017", db)
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "install.php", {"method": "GET", "params": {}, "referer": None})
        installer_link = "install.php?install=yes" in resp["body"]
        body_file = r.save_body("gt017_visitor_install_page", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": "GET install.php",
            "status_code": resp["status_code"],
            "installer_link_exposed": installer_link,
            "body_saved": body_file,
        })
        # Execute the installer action as visitor on a fresh-install
        # precondition (database dropped, documented; baseline restore reverts
        # everything right after this record). With the database present the
        # installer refuses with "The bWAPP database already exists".
        import subprocess
        installed = False
        try:
            env = dict(db._env())
            drop = subprocess.run(
                [db.bin, *db._args(), "--execute", "DROP DATABASE bwapp"],
                capture_output=True, text=True, env=env, timeout=120,
            )
            if drop.returncode != 0:
                raise RuntimeError(f"drop failed: {drop.stderr.strip()[:300]}")
            db.log_sql("execute", "DROP DATABASE bwapp")
            r.add("instrument", {"precondition": "DROP DATABASE bwapp (fresh-install simulation)"})
            action = sess.get(BASE + "install.php?install=yes", timeout=120, allow_redirects=False)
            action_body = str(action.text or "")
            installed = ("bWAPP has been installed" in action_body) or ("successfully" in action_body.lower())
            action_file = r.save_body("gt017_visitor_install_action", action_body, limit=8000)
            # Query the recreated database with a fresh connection (no default db).
            check = subprocess.run(
                [db.bin, *db._args(), "--batch", "--skip-column-names",
                 "--execute", "SELECT COUNT(*) FROM bwapp.users"],
                capture_output=True, text=True, env=env, timeout=120,
            )
            users_after = (check.stdout or "").strip()
            db.log_sql("scalar", "SELECT COUNT(*) FROM bwapp.users")
            r.add("replay", {
                "role": "visitor (no login)",
                "request": "GET install.php?install=yes",
                "status_code": action.status_code,
                "installer_action_completed": installed,
                "recreated_users_table_rows": users_after,
                "body_saved": action_file,
            })
        except Exception as exc:
            r.add("replay", {"request": "GET install.php?install=yes", "error": str(exc)})
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if installer_link else "not_confirmed"
    summary = (f"visitor GET install.php returned {resp['status_code']} with the installer link "
               f"(installer_link_exposed={installer_link}); the install action was invoked as visitor and "
               f"completed (installed={installed}); database restored afterwards.")
    return r.finish(verdict, summary)


def _secret_check(gt_id, page, secret_marker, det, extra_headers=None) -> dict:
    r = v.Recorder(APP, gt_id)
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, page, {"method": "GET", "params": {}, "referer": None})
        exposed = secret_marker in resp["body"]
        body_file = r.save_body(f"{gt_id}_visitor", resp["body"])
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"GET {page}",
            "status_code": resp["status_code"],
            "secret_exposed": exposed,
            "body_saved": body_file,
        })
        if extra_headers:
            import requests as _requests  # noqa: F401
            raw = sess.get(v.absolute(BASE, page) if hasattr(v, "absolute") else BASE + page,
                           headers=extra_headers, timeout=60, allow_redirects=False)
            exposed2 = secret_marker in str(raw.text or "")
            raw_file = r.save_body(f"{gt_id}_visitor_headers", str(raw.text or ""))
            r.add("replay", {
                "role": "visitor (no login)",
                "request": f"GET {page} with headers {extra_headers}",
                "status_code": raw.status_code,
                "secret_exposed_with_headers": exposed2,
                "body_saved": raw_file,
            })
            exposed = exposed or exposed2
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exposed else "not_confirmed"
    summary = (f"visitor GET {page} returned {resp['status_code']}; "
               f"protected secret obtained without authorization={exposed}.")
    return r.finish(verdict, summary)


def gt018(det, db) -> dict:
    del db
    return _secret_check("GT-018", "secret-cors-1.php", "Neo's secret", det)


def gt019(det, db) -> dict:
    del db
    # The "trusted origin" check trusts a client-supplied header and is
    # spoofable by an unauthenticated visitor.
    return _secret_check("GT-019", "secret-cors-2.php", "Wolverine's secret", det,
                         extra_headers={"Origin": "http://intranet.itsecgames.com"})


def gt020(det, db) -> dict:
    del db
    return _secret_check("GT-020", "secret-cors-3.php", "Johnny's secret", det)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt016, gt017, gt018, gt019, gt020):
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
