"""Synchronize canonical ground-truth metadata and retained evidence text."""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parents[2] / "ground_truth.csv"

EV = "ground_truth/audit"

NEW_EVIDENCE = {
    "GT-001": "runs/awcm/analysis/findings.json records the normalized page m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1 as vulnerable for a visitor. Manual verification (evidence: {EV}/awcm/evidence/GT-001.json): as visitor, GET m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500 returned HTTP 200 and exposed the member avatar update form. The archived response body preserves the observed protected content.",
    "GT-002": "The AWCM run records member.php?id=p1 as accessible to user1 with HTTP 200 and no denial evidence. Manual verification with marker token (evidence: {EV}/awcm/evidence/GT-002.json): logged in as user1, GET member.php?id=1 returned HTTP 200 and the response contained the token inserted into the administrator (id=1) title field, confirming user1 obtained administrator profile data. Database restored to its baseline after the record.",
    "GT-003": "runs/awcm/analysis/findings.json records HTTP 200 without redirect or denial and horizontal override id=3. Manual verification with marker token (evidence: {EV}/awcm/evidence/GT-003.json): logged in as user1, GET member.php?id=3 returned HTTP 200 and the response contained the token inserted into user2's (id=3) signature field, confirming user1 obtained another member's protected profile data. Database restored to its baseline after the record.",
    "GT-004": "runs/awcm/analysis/findings.json records HTTP 200 without redirect or denial marker for the installation entry point. Manual verification (evidence: {EV}/awcm/evidence/GT-004.json): as visitor, GET install/index.php returned HTTP 200 with the language-selection installer form and GET install/step1.php?lang=en.php returned HTTP 200 with the next installer step; both response bodies are archived in the evidence directory. Database restored to its baseline after the record.",
    "GT-005": "runs/awcm/analysis/findings.json records HTTP 200 without redirect or denial for the database-backup endpoint. Manual verification with marker token (evidence: {EV}/awcm/evidence/GT-005.json): as visitor, GET control/db_backup.php returned HTTP 200 with a Content-Disposition SQL attachment, and the dump exposed the instrumented awcm_members marker-row token plus the full table data. Database restored to its baseline after the record.",

    "GT-006": "runs/phpoll/analysis/findings.json records a visitor POST receiving HTTP 200 without redirect or denial. Manual verification with marker tokens (evidence: {EV}/phpoll/evidence/GT-006.json): as visitor, POST admin/modifica_band.php returned HTTP 200 and changed band row id=69 nome_band from token1 to token2 in phpoll_test_band without any administrator session. Database restored to its baseline after the record.",
    "GT-007": "runs/phpoll/analysis/findings.json records a visitor POST receiving HTTP 200 without redirect or denial. Manual verification with marker tokens (evidence: {EV}/phpoll/evidence/GT-007.json): as visitor, POST admin/modifica_configurazione.php returned HTTP 200; phpoll_test_configurazione was truncated and rewritten with attacker-supplied values (oggetto_email changed from token1 to token2), and the regenerated img/barra*.gif files were restored after the test. Database restored to its baseline after the record.",
    "GT-008": "runs/phpoll/analysis/findings.json records a visitor POST receiving HTTP 200 without redirect or denial. Manual verification with marker token (evidence: {EV}/phpoll/evidence/GT-008.json): as visitor, POST admin/modifica_votanti.php returned HTTP 200 and deleted the instrumented voter row (id=9, ip=token) from phpoll_test_voti without any administrator session. Database restored to its baseline after the record.",

    "GT-009": "runs/phpns/analysis/findings.json records HTTP 200 without redirect or denial for the installer. Manual verification (evidence: {EV}/phpns/evidence/GT-009.json): as visitor, GET install/index.php returned HTTP 200 with the phpns installation wizard (license step, form action index.php?step=1); the response body is archived in the evidence directory. Database restored to its baseline after the record.",
    "GT-010": "runs/phpns/analysis/findings.json records the register actor receiving HTTP 200 without redirect or denial for this page. Manual verification with marker token (evidence: {EV}/phpns/evidence/GT-010.json): logged in as the low-privilege register account, GET article.php?do=comments&id=6 returned HTTP 200 and the moderation list exposed the token inserted into comment id=5 of article 6. Database restored to its baseline after the record.",
    "GT-011": "runs/phpns/analysis/findings.json records the unauthorized POST receiving HTTP 200 without redirect or denial. Manual verification with marker token (evidence: {EV}/phpns/evidence/GT-011.json): logged in as the low-privilege register account, POST article.php?action=delete&do=comments&id=6 returned HTTP 200 and deleted the instrumented comment row (id=24, comment=token) of article 6 from phpns_comments. Database restored to its baseline after the record.",
    "GT-012": "runs/phpns/analysis/findings.json records HTTP 200 without denial and horizontal override id=6 for article.php?do=edit. Manual verification with marker token (evidence: {EV}/phpns/evidence/GT-012.json): logged in as user1 (not the author), GET article.php?do=edit&id=6 returned HTTP 200 and the edit form exposed the token inserted into user2's article 6 article_text. Database restored to its baseline after the record.",
    "GT-013": "The phpns run artifacts contain the paired article edit workflow and repair context for article.php. Manual verification with marker tokens (evidence: {EV}/phpns/evidence/GT-013.json): logged in as user1, POST article.php?do=editp returned HTTP 200; phpns_articles row id=6 article_text changed from token1 to token2 and article_author was overwritten from user2 to user1, proving the cross-owner update. Database restored to its baseline after the record.",
    "GT-014": "runs/phpns/analysis/findings.json records HTTP 200 without denial and horizontal override id=6 for user.php?do=edit. Manual verification with marker token (evidence: {EV}/phpns/evidence/GT-014.json): logged in as user1, GET user.php?do=edit&id=11 returned HTTP 200 and the account-edit form exposed the token inserted into user2's full_name field (the endpoint text id=6 refers to the original deployment; in the current database user2's account id is 11). Database restored to its baseline after the record.",
    "GT-015": "The phpns run artifacts contain the paired user edit workflow and repair context for user.php. Manual verification with marker tokens (evidence: {EV}/phpns/evidence/GT-015.json): logged in as user1, POST user.php?do=editp returned HTTP 200; phpns_users row id=11 (user2) full_name changed from token1 to token2, proving the cross-user update. Database restored to its baseline after the record.",

    "GT-016": "runs/bwapp/analysis/findings.json records HTTP 200 without redirect or denial marker. Manual verification (evidence: {EV}/bwapp/evidence/GT-016.json): as visitor, GET backdoor.php returned HTTP 200 exposing the NSA file uploader form (response archived in the evidence directory); the upload POST itself redirects a sessionless visitor to login.php. Database restored to its baseline after the record.",
    "GT-017": "runs/bwapp/analysis/findings.json records HTTP 200 without redirect or denial marker. Manual verification (evidence: {EV}/bwapp/evidence/GT-017.json): as visitor, GET install.php returned HTTP 200 exposing the installer link; on a fresh-install precondition (database dropped for the test), GET install.php?install=yes as visitor completed the installation and recreated the bWAPP database with 2 default user rows. Database restored to its baseline after the record.",
    "GT-018": "runs/bwapp/analysis/findings.json records HTTP 200 without redirect or denial. Manual verification (evidence: {EV}/bwapp/evidence/GT-018.json): as visitor, GET secret-cors-1.php returned HTTP 200 and the response body contains the protected secret text (Neo's secret: Oh why didn't I took that BLACK pill?); the secret-bearing response is archived in the evidence directory. Database restored to its baseline after the record.",
    "GT-019": "runs/bwapp/analysis/findings.json records HTTP 200 without redirect or denial. Manual verification (evidence: {EV}/bwapp/evidence/GT-019.json): the trusted-origin check trusts the client-supplied Origin header; as visitor, GET secret-cors-2.php without Origin returned the plain page, while the same request with a spoofed Origin: http://intranet.itsecgames.com header returned HTTP 200 with the protected secret (Wolverine's secret: What's a Magneto?); both responses are archived in the evidence directory. Database restored to its baseline after the record.",
    "GT-020": "runs/bwapp/analysis/findings.json records HTTP 200 without redirect or denial. Manual verification (evidence: {EV}/bwapp/evidence/GT-020.json): as visitor, GET secret-cors-3.php returned HTTP 200 and the response body contains the protected secret text (Johnny's secret: I'm the Ghost Rider!); the secret-bearing response is archived in the evidence directory. Database restored to its baseline after the record.",

    "GT-024": "runs/scarf/analysis/findings.json records HTTP 200 without redirect or denial marker. Manual verification (evidence: {EV}/scarf/evidence/GT-024.json): as visitor, GET install.php returned HTTP 200 with the installer form; the visitor-triggered install (POST with confirmdrop) dropped and recreated the scarf database: the instrumented options marker row disappeared (1 -> 0) and the default Conference Name option was reseeded. config.php and the database were restored to their baselines after the record.",
    "GT-025": "runs/scarf/analysis/findings.json records HTTP 200 without redirect or denial for visitor user1 and user2; the role duplicates are consolidated into one vulnerable operation. Manual verification with marker token (evidence: {EV}/scarf/evidence/GT-025.json): GET comments.php returned HTTP 200 for visitor, user1, and user2 and each response exposed the token of the instrumented pending comment (approved=0). Database restored to its baseline after the record.",
    "GT-026": "runs/scarf/analysis/findings.json records HTTP 200 without redirect or denial for visitor user1 and user2. Manual verification with marker tokens (evidence: {EV}/scarf/evidence/GT-026.json): as visitor, POST generaloptions.php returned HTTP 200 and changed the global option Conference Name from token1 to token2 in the scarf options table. Database restored to its baseline after the record.",

    "GT-027": "runs/events_lister/analysis/findings.json records HTTP 200 without redirect or denial for the setup entry point. Manual verification with marker token (evidence: {EV}/events_lister/evidence/GT-027.json): as visitor, POST admin/setup.php returned HTTP 200; on a fresh-install precondition (admin row cleared for the test) the visitor recreated the administrator account (id=1, uname=token@example.test) with attacker-chosen credentials and the setup inserted a Test Event row (21 -> 22 events). Database restored to its baseline after the record.",
    "GT-028": "runs/events_lister/analysis/findings.json records an unauthenticated POST receiving HTTP 200 without redirect or denial. Manual verification with marker token (evidence: {EV}/events_lister/evidence/GT-028.json): as visitor, POST admin/user_add.php returned HTTP 200 and created a new administrator account row (id=4, uname=token@example.test) in the admin table without any login. Database restored to its baseline after the record.",

    "GT-029": "runs/mybb/analysis/findings.json and replay_response_review.md identify the known target and record HTTP 200 without denial; the unauthorized user was able to invoke the subscription workflow. Manual verification (evidence: {EV}/mybb/evidence/GT-029.json): forum 2 (My Forum) is password-protected (forumdisplay.php shows user1 the password gate); user1 GET usercp2.php?action=addsubscription&fid=2&type=forum returned HTTP 200 and created the mybb_forumsubscriptions row (fid=2, uid=2) without ever supplying the forum password. Database restored to its baseline after the record.",
}


METADATA_UPDATES = {
    "GT-001": {
        "Endpoint / Operation": "m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1",
        "Operation Type": "Resource Access",
        "Expected Authorization Requirement": "Only an authenticated member may open the member avatar control.",
        "Unauthorized Test Case": "Request m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500 as a visitor without an authenticated member session.",
    },
}


def main() -> None:
    with open(CSV_PATH, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = [dict(row) for row in reader]

    updated = 0
    for row in rows:
        gt_id = row["ID"]
        if gt_id in METADATA_UPDATES:
            row.update(METADATA_UPDATES[gt_id])
        if gt_id in NEW_EVIDENCE:
            row["Supporting Evidence"] = NEW_EVIDENCE[gt_id].format(EV=EV)
            updated += 1

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"updated {updated} rows; wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
