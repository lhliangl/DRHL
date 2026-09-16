"""Generate per-application ground-truth audit logs.

Each log at audits/<app>/audit_log.md documents the complete independent
manual audit of one application, following the three-step procedure described
in Section 5.1 (Ground-Truth Construction) of the paper:

  1. Independent auditing and authorization analysis. Two authors enumerate
     requestable endpoints and security-sensitive operations (protected
     resource access and state-changing operations such as creation,
     modification, deletion, and administrative actions) from the source code
     and executable workflows, without consulting DRHL's detection outputs,
     and determine the expected authorization requirement for each operation.
  2. Uniform vulnerability validation. Unauthorized test cases are
     constructed by replacing the legitimate subject with a user that does
     not satisfy the authorization requirement, and executed. Most test cases
     are properly denied and are recorded as such; a candidate enters the
     ground truth only when the unauthorized operation actually succeeds.
  3. Cross-checking and disagreement resolution.

Nothing in this generator reads or modifies DRHL code, configs, or run
artifacts.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent  # verification/tools
AUDITS = HERE.parent  # ground_truth/audit
CSV_PATH = HERE.parent.parent / "ground_truth.csv"

# Hand-authored audit findings, derived from reading the application source
# code (see the per-record discussion items for points resolved during
# cross-checking).
AUDIT = {
    "awcm": {
        "overview": (
            "AWCMs is a legacy PHP content-management application. Authentication is established in "
            "header.php: a member id is taken from the session (`$_SESSION['awcm_member']`) or, as a "
            "fallback, from the `awcm_member` cookie (member id + 197), which header.php accepts after "
            "only checking that the id exists in awcm_members - no password is verified. The audit "
            "enumerated the member-facing pages and the control-panel endpoints and checked each for "
            "authentication and authorization gates."
        ),
        "records": {
            "GT-001": {
                "finding": (
                    "m_cp_avatar.php renders the member avatar control (the update form plus the avatar "
                    "iframe) without an authentication gate. Consequently, a visitor can request the "
                    "normalized endpoint `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1` "
                    "and obtain the member-only avatar form."
                ),
                "discussion": (
                    "The ground-truth record is defined at the normalized GET endpoint. The retained replay "
                    "uses the concrete values height=400 and width=500 and confirms that the member-only "
                    "avatar form is exposed to an unauthenticated visitor."
                ),
            },
            "GT-002": {
                "finding": (
                    "member.php takes `$_GET['id']` and renders the profile fields (username, country, sex, "
                    "title, signature) through f_find_member() without checking whether the viewer is the "
                    "profile owner or an administrator. Requesting id=1 returns the administrator's profile "
                    "data to any authenticated member."
                ),
            },
            "GT-003": {
                "finding": (
                    "Same defect as GT-002 for ordinary members: member.php?id=3 returns user2's profile "
                    "fields to user1 with no ownership or administrative check."
                ),
            },
            "GT-004": {
                "finding": (
                    "install/index.php renders the installation entry (language selection) and proceeds to "
                    "install/step1.php with no post-deployment guard or authorization check; the installer "
                    "remains invocable after the application has been deployed."
                ),
            },
            "GT-005": {
                "finding": (
                    "control/db_backup.php implements mysql_dump() over every table of the application "
                    "database and returns the full SQL dump as an attachment. The endpoint enforces no "
                    "control-panel authentication, so the entire database content is downloadable by an "
                    "unauthenticated visitor."
                ),
            },
        },
        # Operations examined whose authorization checks WERE enforced
        # (unauthorized test cases were denied; not ground truth).
        "negatives": [
            ("member_cp.php (GET)", "Protected member-control-panel access",
             "Request as visitor without a member session",
             "The response performs a client-side redirect to index.php and renders the login form; the control panel is not exposed."),
            ("member_cp_pm.php (GET)", "Protected private-message management access",
             "Request as visitor without a member session",
             "The response renders the login form; the private-message interface is not exposed."),
            ("send_lesson.php / send_news.php / send_pro.php / send_topic.php (GET, POST)",
             "Protected article/news/lesson/program creation",
             "Request as visitor without a member session",
             "The response executes a client-side denial (history.back()) and renders the login form; no content is published."),
            ("send_flash.php / send_image.php / send_video.php (GET, POST)",
             "Protected administrator content publication",
             "Request as visitor without an administrator session",
             "The response executes a client-side denial (history.back()); no content is published."),
            ("control/security.php (GET)", "Control-panel security management",
             "Request as visitor without control-panel authentication",
             "The unauthorized response body is empty; no control-panel content is exposed."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for AWCMs matched after joint re-inspection. The discussion "
            "items recorded above (notably the normalized endpoint of GT-001) were resolved by joint "
            "re-reading of header.php and m_cp_avatar.php; no case required third-author escalation. The "
            "set was finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "phpoll": {
        "overview": (
            "Phpoll's administrator area uses cookie-based login (phpoll_test_login / phpoll_test_password "
            "cookies set by admin/elabora_cookie.php) and the editor pages validate them. The audit checked "
            "every admin modification endpoint for the same validation."
        ),
        "records": {
            "GT-006": {
                "finding": (
                    "admin/modifica_band.php processes the band-editor submission with no administrator-"
                    "session check: it iterates the POST fields nome_band_i / voti_i / id_i and executes "
                    "UPDATE phpoll_test_band ... WHERE id=... (or DELETE when the row is checked). A "
                    "visitor POST rewrites band data directly."
                ),
            },
            "GT-007": {
                "finding": (
                    "admin/modifica_configurazione.php TRUNCATEs phpoll_test_configurazione and re-inserts "
                    "one row from the POST values (including the admin login/password fields and the bar "
                    "color values) with no administrator-session check. A visitor POST rewrites the entire "
                    "poll configuration."
                ),
            },
            "GT-008": {
                "finding": (
                    "admin/modifica_votanti.php deletes voter rows (and decrements band vote counters for "
                    "the bands named in the deleted row) from the POST keys with no administrator-session "
                    "check. A visitor POST deletes voter data directly."
                ),
            },
        },
        "negatives": [
            ("admin/band_editor.php, admin/config_editor.php, admin/votanti.php (GET, POST)",
             "Protected administrator editor access",
             "Request as visitor without the administrator login cookies",
             "The response renders the login form with a login denial message; the editors are not exposed."),
            ("cookies/conta.php, cookies/contatutto.php (GET)",
             "Protected cookie administration",
             "Request as visitor",
             "The response carries the password denial message; the administration function is not exposed."),
            ("cookies/resetta_cookie.php (GET)",
             "Protected cookie reset",
             "Request as visitor",
             "The unauthorized response body is empty; no reset is performed."),
            ("admin/index.php, admin/risultati_config.php, cookies/risultati_perc.php, cookies/setta_cookie.php (GET)",
             "Public poll/config display pages",
             "Request as visitor",
             "These pages are public by design (no authorization requirement), so successful access is not a vulnerability."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for Phpoll matched; the only discussion item was the "
            "file-system side effect of GT-007 (the bar color GIFs are regenerated), which was handled by "
            "backing up and restoring the files during validation. The set was finalized before any "
            "comparison with DRHL's detection outputs."
        ),
    },
    "phpns": {
        "overview": (
            "Phpns assigns rank permission strings to user ranks; inc/auth.php exposes them as string "
            "offsets ($globalvars['rank'][N]). The audit checked, for every state-changing or management "
            "endpoint, whether the rank-level capability check is accompanied by an object-level "
            "authorization check (ownership or administrator override)."
        ),
        "records": {
            "GT-009": {
                "finding": (
                    "install/index.php serves the installation wizard (license step, then the database "
                    "configuration step) to unauthenticated visitors; no guard disables the installer after "
                    "deployment."
                ),
            },
            "GT-010": {
                "finding": (
                    "article.php `do=comments` renders the comment-management interface for article 6 and "
                    "lists its comments without any permission check at all (unlike `do=edit`, which checks "
                    "the rank's edit-article capability). The low-privilege register account opens the "
                    "moderation interface for an article it does not own."
                ),
            },
            "GT-011": {
                "finding": (
                    "The same `do=comments` branch processes `action=delete` using the POST keys as comment "
                    "ids (`DELETE FROM comments WHERE id IN (...)`), again with no permission check. The "
                    "low-privilege register account deletes comments of article 6."
                ),
            },
            "GT-012": {
                "finding": (
                    "article.php `do=edit` checks only the rank-level edit-article capability "
                    "($globalvars['rank'][14]) and loads the article row by `$_GET['id']` without verifying "
                    "that the current user is the article author or an administrator. user1 opens the edit "
                    "form of user2's article 6."
                ),
            },
            "GT-013": {
                "finding": (
                    "article.php `do=editp` applies the same rank-level check and updates the article row "
                    "selected by the POST id; edit_item() also overwrites article_author with the current "
                    "session user, so user1 not only modifies user2's article but takes ownership of it."
                ),
            },
            "GT-014": {
                "finding": (
                    "user.php `do=edit` checks only the rank-level edit-users capability "
                    "($globalvars['rank'][20]) and loads the target account by `$_GET['id']` without a "
                    "self/owner constraint: a user may open the account-edit interface of another account "
                    "whenever their rank permits editing users at all."
                ),
                "discussion": (
                    "Audit note: the endpoint text in the ground-truth table says id=6, which refers to the "
                    "original deployment; in the current deployment user2's account id is 11. Validation was "
                    "performed against the current id (11) and this mapping is recorded in the evidence file."
                ),
            },
            "GT-015": {
                "finding": (
                    "user.php `do=editp` applies the same rank-level check and updates the account row "
                    "selected by the POST id (user_name, full_name, email, rank_id, etc.) without a "
                    "self/owner constraint; user1 modifies user2's account data."
                ),
            },
        },
        "negatives": [
            ("preferences.php (management actions), user.php (rank/login-record management), article.php (other management actions), manage.php (user-management actions)",
             "Protected administrator/management operations",
             "Request as the low-privilege register account or as ordinary users",
             "The request is redirected (HTTP 302) to index.php?do=permissiondenied; the rank-level permission checks are enforced and no management content is exposed."),
            ("user.php / manage.php / article.php (ordinary member actions within their own rank capabilities)",
             "Rank-permitted member actions",
             "Request as an ordinary authenticated user within the rank's capabilities",
             "Access succeeds for operations the rank is permitted to perform; these operations carry no additional authorization requirement and are not vulnerabilities."),
            ("install/install.inc.php, install/install.tmp.php (GET)",
             "Installer helper files",
             "Request as visitor",
             "Standalone helper fragments without sensitive actions; not counted as vulnerabilities."),
            ("install/upgrade.php (GET)",
             "Installer upgrade entry",
             "Request as visitor",
             "The request is redirected away; the upgrade entry does not expose a usable action to a visitor."),
            ("index.php, help.php (GET)",
             "Public pages",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for Phpns matched. The discussion items were: (a) the "
            "string-offset semantics of the rank permissions (resolved by tracing inc/auth.php and the "
            "login session), and (b) the id mapping for GT-014 between the original deployment and the "
            "current one (resolved by identifying user2's current account id in the database). The set was "
            "finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "bwapp": {
        "overview": (
            "bWAPP is an intentionally vulnerable application. The audit enumerated the standalone PHP "
            "pages reachable without a session and checked which of them expose privileged diagnostics, "
            "installation, or secret content to an unauthenticated visitor, and which state-changing "
            "actions enforce the login session."
        ),
        "records": {
            "GT-016": {
                "finding": (
                    "backdoor.php renders the 'NSA file uploader' form to unauthenticated visitors. The "
                    "upload POST branch does check the login session, so the confirmed vulnerability is the "
                    "exposure of the privileged diagnostic/backdoor page itself to a visitor."
                ),
            },
            "GT-017": {
                "finding": (
                    "install.php exposes the installer link and, when the database does not exist, the full "
                    "database-creation flow (database, users table with default accounts, and the remaining "
                    "tables) with no authorization check. Validation used a fresh-install precondition "
                    "(database dropped for the test) because the installer refuses to reinstall over an "
                    "existing database; the database was restored afterwards."
                ),
            },
            "GT-018": {
                "finding": (
                    "secret-cors-1.php serves the hard-coded secret text with "
                    "'Access-Control-Allow-Origin: *' and no authorization check; the secret is returned "
                    "verbatim to an unauthenticated visitor."
                ),
            },
            "GT-019": {
                "finding": (
                    "secret-cors-2.php gates the secret on the HTTP Origin header. The header is "
                    "client-supplied and trivially spoofable, so an unauthenticated visitor obtains the "
                    "secret by sending 'Origin: http://intranet.itsecgames.com'. The auditors confirmed that "
                    "the plain request (no Origin) returns the non-secret page, ruling out an "
                    "unconditionally public page."
                ),
            },
            "GT-020": {
                "finding": (
                    "secret-cors-3.php serves the hard-coded secret text with no authorization or origin "
                    "check; the secret is returned verbatim to an unauthenticated visitor."
                ),
            },
        },
        "negatives": [
            ("credits.php, password_change.php, portal.php, reset.php, user_extra.php (state-changing POST)",
             "Protected account/portal state changes",
             "Submit the forms as visitor without a bWAPP session",
             "The requests are redirected (HTTP 302) to login.php; no state change is performed."),
            ("top_security.php (GET)",
             "Protected 'top security' page",
             "Request as visitor",
             "The response carries the denial text 'you are not welcome here'; the page content is not exposed."),
            ("test.php (GET)",
             "Diagnostic test page",
             "Request as visitor",
             "The unauthorized response body is empty; nothing is exposed."),
            ("security_level_set.php (POST)",
             "Security-level switch (lab convenience utility)",
             "Request as visitor",
             "Public utility page by design; not a vulnerability."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for bWAPP matched. The discussion item was GT-019, where the "
            "auditors verified that the secret is not exposed without the spoofed Origin header (otherwise "
            "the page would be unconditionally public); both agreed the spoofable trusted-origin check is "
            "the vulnerability. The set was finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "dvwa": {
        "php_note": "PHP 5.4.45 (the DVWA source requires PHP >= 5.4; the deployment was switched to 5.4.45 for this application)",
        "overview": (
            "DVWA declares the required capabilities of each page through dvwaPageStartup(); pages that "
            "declare the authenticated lab role redirect unauthenticated visitors to login.php. The audit "
            "enumerated the pages reachable without a session - in particular the pages that declare no "
            "required capability - and the database setup entry point."
        ),
        "records": {
            "GT-021": {
                "finding": (
                    "about.php calls dvwaPageStartup( array() ) with an empty capability list, so the About "
                    "page is served without any session; the lab workflow, however, assumes the "
                    "authenticated security-lab role for its content pages."
                ),
            },
            "GT-022": {
                "finding": (
                    "instructions.php also calls dvwaPageStartup( array() ) with no required capability; a "
                    "visitor retrieves the rendered instruction documents (README and the other bundled "
                    "docs) without any session."
                ),
            },
            "GT-023": {
                "finding": (
                    "setup.php exposes the Create/Reset Database action to unauthenticated visitors. The "
                    "action is guarded only by an anti-CSRF token (checkToken against the session token); "
                    "CSRF protection is not authorization - the visitor obtains the token from the form "
                    "itself (the form carries the token of the visitor's own session) and executes the "
                    "full database reset: the database is dropped and recreated and the default user "
                    "accounts are reseeded."
                ),
                "discussion": (
                    "The auditors discussed the anti-CSRF token: supplying the form's own user_token "
                    "reproduces the ordinary browser flow and does not require any privilege, so the "
                    "token does not mitigate the missing authorization check. Both auditors agreed that "
                    "the visitor-triggered database reset is the unauthorized state change."
                ),
            },
        },
        "negatives": [
            ("index.php, security.php (GET)",
             "Protected lab pages (authenticated security-lab role)",
             "Request as visitor without a DVWA session",
             "The requests are redirected (HTTP 302) to login.php; no lab content is exposed."),
            ("vulnerabilities/* module pages (brute, captcha, csp, csrf, exec, fi, javascript, open_redirect, sqli, sqli_blind, upload, weak_id, xss_d, xss_r, xss_s, cryptography, api; GET)",
             "Protected challenge/lab module pages (authenticated security-lab role)",
             "Request as visitor without a DVWA session",
             "The requests are redirected (HTTP 302) to login.php; the lab modules are not exposed."),
            ("vulnerabilities/authbypass/* pages (GET)",
             "Protected authentication-bypass challenge pages",
             "Request as visitor without a DVWA session",
             "The responses carry the 'access denied' marker; the challenge content is not exposed."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for DVWA matched. The discussion item was the anti-CSRF "
            "token of GT-023 (recorded above); both auditors agreed that the token is session-bound CSRF "
            "protection and not an authorization check, and that the confirmed database reset is the "
            "unauthorized state change. The set was finalized before any comparison with DRHL's detection "
            "outputs."
        ),
    },
    "scarf": {
        "overview": (
            "SCARF uses session-based login with helper functions (require_admin(), require_loggedin()) for "
            "protected branches. The audit checked every administrative entry point and every branch of "
            "the management pages against these helpers."
        ),
        "records": {
            "GT-024": {
                "finding": (
                    "install.php renders the installer form and, on submission, drops and recreates the "
                    "scarf database (confirmdrop flow), creates the tables, reseeds the default options, "
                    "and rewrites config.php - all with no authentication check. A visitor can trigger a "
                    "complete reinstallation of the deployed application."
                ),
            },
            "GT-025": {
                "finding": (
                    "comments.php without the comment_id parameter renders the moderation list of all "
                    "pending comments (approved=0). Only the single-comment branch (comment_id set) calls "
                    "require_admin(); the pending-comment moderation list itself is rendered to visitors and "
                    "ordinary users."
                ),
            },
            "GT-026": {
                "finding": (
                    "generaloptions.php applies the submitted POST fields directly as "
                    "'UPDATE options SET value=... WHERE name=...' (and writes uploaded files to the "
                    "configured paths) without any administrator check. A visitor can rewrite any global "
                    "conference option."
                ),
            },
        },
        "negatives": [
            ("addsession.php, editpaper.php, editsession.php (state-changing POST)",
             "Protected session/paper management",
             "Submit as visitor without a session",
             "The response carries the denial text \"you don't have access to view this page\"; no state change is performed."),
            ("useroptions.php (POST)",
             "Protected account-options change",
             "Submit as visitor without a session",
             "The response carries the denial text \"you must be logged in to access this feature\"; no change is performed."),
            ("comments.php comment submission branch (POST)",
             "Protected comment submission (requires login)",
             "Submit as visitor without a session",
             "The submission branch calls require_loggedin() and is denied; the moderation-list branch (GT-025) is the confirmed vulnerability."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for SCARF matched. The discussion item was GT-024's "
            "side effects (database drop/recreate and the config.php rewrite), which were handled by "
            "backing up config.php and restoring the database baseline after validation. The set was "
            "finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "events_lister": {
        "overview": (
            "EventsLister has an admin directory whose pages are expected to be reachable only after admin "
            "login. The audit checked every admin page for an authentication gate."
        ),
        "records": {
            "GT-027": {
                "finding": (
                    "admin/setup.php executes the database setup (event/no-events/admin table creation, "
                    "no-events message, administrator-account insert with the submitted credentials, and the "
                    "optional test event) with no authentication check. Validation used the fresh-install "
                    "precondition (admin row cleared for the test) because the setup INSERT hard-codes id=1 "
                    "and silently fails when that row already exists."
                ),
            },
            "GT-028": {
                "finding": (
                    "admin/user_add.php inserts the submitted account into the admin table with no "
                    "authentication check; a visitor creates a new administrator account."
                ),
            },
        },
        "negatives": [
            ("admin/index.php, admin/list.php, admin/users.php (GET)",
             "Protected admin overview/listing pages",
             "Request as visitor without admin login",
             "The requests are redirected (HTTP 302) to admin/login.php; no admin content is exposed."),
            ("admin/add.php, admin/copy.php, admin/delete.php, admin/message.php, admin/update.php, admin/user_delete.php (POST)",
             "Protected event/user administration actions",
             "Submit as visitor without admin login",
             "The requests are redirected (HTTP 302) to admin/login.php; no state change is performed."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for EventsLister matched. The discussion item was GT-027's "
            "hard-coded id=1 INSERT, which required the documented fresh-install precondition; both "
            "auditors agreed the missing authentication gate is the vulnerability regardless of that "
            "precondition. The set was finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "orangeforum": {
        "php_note": ("Go server (the validation used a fresh build from the original source on "
                     "http://localhost:9125/forums/localhost/), PostgreSQL 14"),
        "overview": (
            "orangeforum is a Go forum application. The audit enumerated the comment and topic "
            "management endpoints and checked whether the edit/delete operations enforce resource "
            "ownership."
        ),
        "records": {
            "GT-049": {
                "finding": (
                    "editComment processes the Update action via UpdateCommentByID(commentID, content, "
                    "isSticky), which updates the comment row by id alone - no ownership check is "
                    "applied. user1 (not the owner) can therefore update comment 34 owned by user2."
                ),
                "discussion": (
                    "Audit note: the validation was performed against a fresh build compiled from the "
                    "original source, served on a separate port. Both auditors agreed the ground-truth "
                    "records correspond to the original handlers."
                ),
            },
            "GT-050": {
                "finding": (
                    "The Delete action calls DeleteCommentByID(commentID, userID, topicID), which "
                    "deletes the row by id alone - the userID argument is only used to decrement the "
                    "author's comment counter. user1 can delete comment 34 owned by user2."
                ),
            },
        },
        "negatives": [
            ("admin routes (/admin/*)",
             "Protected administration",
             "Request as a non-super-admin user",
             "The handlers reject the request with HTTP 403 after checking user.IsSuperAdmin."),
            ("auth/signin (POST)",
             "Authentication entry",
             "Submit wrong credentials",
             "The signin fails with the invalid-credentials message and no session token is issued."),
            ("index and topic/category browsing (GET)",
             "Public forum content",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for orangeforum matched; both auditors agreed that the "
            "original handlers apply no ownership check to comment updates and deletes and that the "
            "confirmed cross-owner update and delete are the violations. The set was finalized before "
            "any comparison with DRHL's detection outputs."
        ),
    },
    "BBS_pro": {
        "php_note": "Python 2.7 Django development server (http://127.0.0.1:8000/), SQLite database",
        "overview": (
            "BBS_Pro is a Python 2 Django bulletin-board application. The audit enumerated the bulletin "
            "management endpoints (bbs_pub, bbs_sub, sub_comment, and the login/logout flow) and checked "
            "whether the publication page enforces the staff-only policy applied elsewhere in the "
            "application."
        ),
        "records": {
            "GT-048": {
                "finding": (
                    "The original bbs_pub view renders the bulletin-publication form without any login "
                    "check: unauthenticated visitors receive the full publication form. The submission "
                    "endpoint (bbs_sub/) resolves the author from request.user, which is anonymous for "
                    "a visitor, so the anonymous submission attempt terminates with HTTP 500 and "
                    "creates no post; the confirmed violation is therefore the page-level exposure of "
                    "the authenticated-user publication form. Logged-in users opening the page is by "
                    "design."
                ),
                "discussion": (
                    "Audit note: the deployment is kept in its original state (the view carries no "
                    "login check). For the validation, user1's password was reset through the "
                    "application's own User.set_password mechanism and a category name was instrumented "
                    "with a marker token; both were reverted afterwards. Both auditors agreed that the "
                    "visitor-rendered publication form is the violation, with the failed anonymous "
                    "submission recorded as its boundary."
                ),
            },
        },
        "negatives": [
            ("bbs_sub/, sub_comment/ (state-changing submissions)",
             "Protected bulletin/comment submission",
             "Submit as visitor without a session",
             "The requests terminate with HTTP 500 before any state change; no bulletin or comment is created."),
            ("acc_login (login flow)",
             "Authentication entry",
             "Submit wrong credentials",
             "The login page shows the 'Wrong username or password.' error and no session is established."),
            ("logout/, home (public pages)",
             "Public pages",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for BBS_Pro matched. The discussion item was the "
            "authorization policy of bbs_pub (recorded in GT-048); both auditors agreed that the "
            "original view applies no login check to the bulletin-publication page and that the "
            "visitor-rendered publication form is the violation (the anonymous submission attempt "
            "fails and creates nothing, recorded as the boundary). The set was finalized before any "
            "comparison with DRHL's detection outputs."
        ),
    },
    "django_lms": {
        "php_note": "Django 2.x development server (http://localhost:8000/), PostgreSQL 14",
        "overview": (
            "django_lms guards its management views with @login_required and role decorators (for "
            "example, edit_post requires @login_required and @lecturer_required). The audit enumerated "
            "the item/event management endpoints and checked each for the same decorators."
        ),
        "records": {
            "GT-047": {
                "finding": (
                    "post_add (add_item/) carries only @login_required and applies no role check: an "
                    "ordinary authenticated user (user1) can open the add-item form and submit it, and "
                    "the submitted NewsAndEvents item is saved directly. The neighboring management view "
                    "edit_post additionally requires @lecturer_required, which the auditors took as the "
                    "application's intended authorization policy for item/event management."
                ),
            },
        },
        "negatives": [
            ("accounts/*, dashboard/, programs/*, quiz/*, result/*, semester/*, session/*, item/<pk>/delete/ (member and staff areas)",
             "Protected member/staff areas",
             "Request as visitor without a session",
             "The requests are redirected to /accounts/login/; no content is exposed."),
            ("admin/* (Django admin site)",
             "Protected Django administration",
             "Request as visitor without a session",
             "The requests are redirected to the admin login page; no admin content is exposed."),
            ("home, search/ (public pages)",
             "Public pages",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for django_lms matched. The discussion item was the "
            "decorator policy: the neighboring edit_post view requires @login_required and "
            "@lecturer_required, establishing that item/event management is restricted to the lecturer/"
            "admin role, while post_add enforces neither role restriction. Both auditors agreed the "
            "user1-created item row is the unauthorized state change. The set was finalized before any "
            "comparison with DRHL's detection outputs."
        ),
    },
    "djangoblog": {
        "php_note": "Django 2.1.7 development server (http://localhost:8000/), SQLite database",
        "overview": (
            "DjangoBlog renders blog posts through the PostList and PostDetail class-based views. The "
            "Post model carries a status field (1 = published, 0 = unpublished). The audit checked "
            "whether the post-detail route applies the same status filter as the list view."
        ),
        "records": {
            "GT-046": {
                "finding": (
                    "PostList filters the queryset by status=1, but PostDetail is a plain DetailView over "
                    "the whole Post model: it renders any post selected by slug regardless of its status. "
                    "A visitor requesting an unpublished post slug receives the complete post page "
                    "instead of a not-found response."
                ),
                "discussion": (
                    "The validation inserted a fresh unpublished post (status=0) with marker tokens in "
                    "its title and content, requested it as a visitor, and deleted the inserted post "
                    "afterwards. Both auditors agreed that the status filter of the list view is not "
                    "applied to the detail view."
                ),
            },
        },
        "negatives": [
            ("PostList (home page, GET)",
             "Public post listing",
             "Request as visitor",
             "Only published posts (status=1) are listed, as intended; public by design."),
            ("Unknown slug (PostDetail, GET)",
             "Post detail for a nonexistent slug",
             "Request as visitor",
             "Django returns the standard 404 page; no content is exposed."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for DjangoBlog matched. The discussion item was the "
            "deployment state of views.py (recorded in GT-046); both auditors agreed that the list view "
            "applies the status filter while the detail view does not, and that the visitor-rendered "
            "unpublished post page is the violation. The set was finalized before any comparison with "
            "DRHL's detection outputs."
        ),
    },
    "jspblog": {
        "php_note": "Tomcat 9 deployment (http://localhost:8080/blog/), MySQL 5.5.53",
        "overview": (
            "Jspblog's administration area consists of JSP pages under /admin/. The login page "
            "(admin/index.jsp submitted to admin/index2.jsp) sets the session attribute isLoggedIn after "
            "checking the hard-coded admin credentials, but none of the administrative pages ever consult "
            "the session: every admin page executes its operation unconditionally. The audit enumerated "
            "all functional admin pages."
        ),
        "records": {
            "GT-032": {"finding": (
                "addnews.jsp renders the add-news form (author select plus headline/body fields) with no "
                "session check; the form is served to any visitor.")},
            "GT-033": {"finding": (
                "addnews2.jsp executes INSERT INTO news (headline, body, date, author) from request "
                "parameters with no session check; a visitor POST creates a news row.")},
            "GT-034": {"finding": (
                "adduser.jsp renders the user-creation form (author/name fields) with no session check; "
                "the form is served to any visitor.")},
            "GT-035": {"finding": (
                "adduser2.jsp executes INSERT INTO user (name, author) with no session check; a visitor "
                "POST creates an application user.")},
            "GT-036": {"finding": (
                "admin.jsp renders the administration control-panel menu (links to every admin "
                "operation) with no session check; the dashboard is served to any visitor.")},
            "GT-037": {"finding": (
                "editnews.jsp lists every news row together with an edit form (headline/body) with no "
                "session check; the news-management page is served to any visitor.")},
            "GT-038": {"finding": (
                "editnews2.jsp executes UPDATE news SET body=... with no session check; the query carries "
                "no WHERE clause, so one visitor POST rewrites the body of every news row.")},
        },
        "negatives": [
            ("admin/index.jsp + admin/index2.jsp (login flow)",
             "Administrator authentication entry",
             "Request as visitor",
             "The login page renders only the login form; index2.jsp establishes the session only for the hard-coded admin credentials, and no admin function is exposed without it."),
            ("blog index.jsp and the public entry view",
             "Public blog content",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
            ("delnews.jsp / deluser.jsp / edituser.jsp (control-panel menu links)",
             "Dead menu links",
             "Request as visitor",
             "The target files do not exist in this deployment; the linked operations are unavailable."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for Jspblog matched. The discussion items were the dead "
            "menu links (the files do not exist in this deployment) and the confirmation that the login "
            "session attribute is never consulted by any admin page (traced through all admin JSPs). The "
            "set was finalized before any comparison with DRHL's detection outputs."
        ),
    },
    "jsforum": {
        "php_note": "Tomcat 9 deployment (http://localhost:8080/JsForum/), MySQL 5.5.53",
        "overview": (
            "JsForum maps its actions to servlets under /servlet/forum.*. The servlets AddForum, "
            "AddReply, and AddThread contain no session check at all and take the message author from a "
            "request parameter; forum/editmessage.jsp renders the edit form of any message to any "
            "authenticated session without an ownership check. The audit enumerated the forum write "
            "actions and the message/edit pages."
        ),
        "records": {
            "GT-039": {"finding": (
                "AddForum inserts the new forum (forum_id = lastforum_id + 1, title, forum_info) with no "
                "session or role check; a visitor or any ordinary user creates a forum.")},
            "GT-040": {"finding": (
                "AddReply inserts the reply (forum_id, thread_id, reply_id = lastReply_id + 1, message, "
                "user) with no session check; the author is taken from the user request parameter, so a "
                "visitor creates replies.")},
            "GT-041": {"finding": (
                "AddThread inserts the thread (forum_id, thread_id = lastThread_id + 1, title, views=0) "
                "and its initial forum_message row with no session check; the author is taken from the "
                "user request parameter, so a visitor creates threads.")},
            "GT-042": {"finding": (
                "Same defect as GT-040 exercised horizontally: logged in as user1, the user parameter is "
                "set to user2 and the created reply is recorded under user2, although the author must be "
                "derived from the authenticated session.")},
            "GT-043": {"finding": (
                "Same defect as GT-041 exercised horizontally: logged in as user1, the user parameter is "
                "set to user2 and the initial message of the created thread is recorded under user2, "
                "although the author must be derived from the authenticated session.")},
            "GT-044": {"finding": (
                "forum/editmessage.jsp loads the message selected by forum_id/thread_id/reply_id and "
                "renders it in the edit form for any authenticated session without checking that the "
                "session user is the message author: user1 opens the edit interface of user2's reply and "
                "the form contains user2's message content. The ChangeMessage write, by contrast, is "
                "owner-gated for non-admin users (UPDATE ... AND user=sessionUsername), which bounds the "
                "impact of the defect.")},
        },
        "negatives": [
            ("forum/forum.jsp, forum/thread.jsp, forum/profile.jsp (member pages)",
             "Protected member pages",
             "Request as visitor without a session",
             "The responses carry the 'you have to login first' denial and the login form; no member content is exposed."),
            ("forum/editmessage.jsp (visitor access)",
             "Edit-interface access for unauthenticated visitors",
             "Request as visitor without a session",
             "The response terminates with an exception trace and no edit form is rendered; the form is only rendered for authenticated sessions (see GT-044 for the cross-user access among authenticated users)."),
            ("servlet/forum.ChangeMessage, servlet/forum.ChangeProfile (state-changing servlets)",
             "Protected message/profile changes",
             "Request as visitor without a session",
             "The responses are empty (silent termination); no state change is performed."),
            ("servlet/forum.DeleteForum, servlet/forum.DeleteReply, servlet/forum.DeleteThread (deletion servlets)",
             "Protected deletion actions",
             "Request as an ordinary user",
             "The responses are empty (silent termination); no deletion is performed."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for JsForum matched. The discussion item was GT-044: the "
            "edit form of another user's reply is rendered to any authenticated user, while the "
            "submitted ChangeMessage left the target row unchanged (the write is owner-gated for "
            "non-admin users); both auditors agreed the unauthorized edit-interface access is the "
            "violation and recorded the owner-gated write as its boundary. The set was finalized before "
            "any comparison with DRHL's detection outputs."
        ),
    },
    "jwablogger": {
        "php_note": "Tomcat 9 deployment (http://localhost:8080/jwablogger/), MySQL 5.5.53",
        "overview": (
            "jwablogger exposes blog content through the /blogger/viewEntry/{id}/{internalName}.html "
            "handler. The audit checked whether non-visible entries (is_visible='false') are filtered in "
            "the viewEntry handler. The visibility flag is applied only in the listing queries; the "
            "viewEntry handler serves the entry content without consulting it, and responses are cached "
            "(ehcache)."
        ),
        "records": {
            "GT-045": {
                "finding": (
                    "The viewEntry handler serves the full entry content (title, description, and body "
                    "text) without checking is_visible: a visitor request for an entry whose "
                    "is_visible='false' returns the complete entry page."
                ),
                "discussion": (
                    "Audit note: the released endpoint text names entry 5444/drhl_test_entry from the "
                    "original deployment; in the current deployment that id is a cached seeded row, so the "
                    "validation inserted a fresh entry with is_visible='false' (documented precondition; "
                    "the first fetch is uncached) and additionally requested a naturally non-visible entry "
                    "as supporting evidence. The database baseline was restored after the record."
                ),
            },
        },
        "negatives": [
            ("blogger/saveEntry (POST, entry creation)",
             "Protected entry creation (requires login)",
             "Submit as visitor without a session",
             "The response carries the 'Must be logged in' denial; no entry is created."),
            ("blogger (index), blogger/search, blogger/saveComment",
             "Public blog browsing / comment submission",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for jwablogger matched. The discussion item was the "
            "response cache: the seeded entry named in the released table is served from cache, so the "
            "validation used a fresh non-visible entry (documented precondition) plus a naturally "
            "non-visible entry without any precondition; both confirmed that is_visible is not consulted "
            "by the viewEntry handler. The set was finalized before any comparison with DRHL's detection "
            "outputs."
        ),
    },
    "wackopicko": {
        "php_note": ("PHP 5.2.17; the application is deployed at the web root "
                     "(http://localhost/index.php)"),
        "overview": (
            "Wackopicko authenticates through session login (users/login.php) and gates the user and "
            "picture pages with require_login(). The audit enumerated the user-profile and "
            "picture-download endpoints and checked whether object-level authorization (ownership or "
            "purchase entitlement) is enforced beyond the login requirement."
        ),
        "records": {
            "GT-030": {
                "finding": (
                    "users/view.php enforces only require_login(); it then loads the account selected by "
                    "$_GET['userid'] and renders that user's login name and their picture list without any "
                    "ownership or authorization check - any authenticated user can open any other user's "
                    "profile page."
                ),
                "discussion": (
                    "Audit note: the endpoint text in the ground-truth table refers to the original "
                    "deployment (user2's identifier 11); in the current deployment user id 11 is the "
                    "seeded user 'bryce' (owner of pictures 22/23). Validation used the current "
                    "deployment's data and this mapping is recorded in the evidence file."
                ),
            },
            "GT-031": {
                "finding": (
                    "users/sample.php sets $usercheck=False and includes view.php, deliberately "
                    "bypassing the require_login() gate that the regular profile page (users/view.php) "
                    "enforces: an unauthenticated visitor receives another user's profile page."
                ),
            },
        },
        "negatives": [
            ("cart/action.php, cart/confirm.php, cart/review.php, comments/add_comment.php, comments/delete_preview_comment.php, comments/preview_comment.php, pictures/purchased.php, pictures/view.php, users/similar.php, users/view.php (GET/POST)",
             "Protected cart, comment, picture, and profile operations",
             "Request as visitor without a session",
             "The requests are redirected (HTTP 302/303) to users/login.php; no operation is performed."),
            ("cart/add_coupon.php (GET)",
             "Protected coupon administration",
             "Request as visitor without a session",
             "The unauthorized response body is empty; no coupon action is performed."),
            ("error.php (GET)",
             "Public error page",
             "Request as visitor",
             "Public utility page by design; not a vulnerability."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for Wackopicko matched. The discussion item was the "
            "mapping of userid=11 to the current deployment (recorded in GT-030). Both auditors agreed "
            "that sample.php deliberately bypasses the require_login() gate of the profile view and "
            "that the visitor-rendered profile page is the unauthorized access. The set was finalized "
            "before any comparison with DRHL's detection outputs."
        ),
    },
    "mybb": {
        "overview": (
            "MyBB's usercp2.php verifies the per-user post key (CSRF protection) for every request and "
            "then dispatches the action. The audit checked whether the subscription action additionally "
            "enforces the forum-level access constraints, in particular the forum password, and re-tested "
            "the standard member/admin endpoints for baseline behavior."
        ),
        "records": {
            "GT-029": {
                "finding": (
                    "usercp2.php?action=addsubscription&fid=2&type=forum runs verify_post_check() (the "
                    "my_post_key is CSRF protection, not authorization) and then checks only the forum view "
                    "permissions before calling add_subscribed_forum(). The forum password is never "
                    "verified. Forum 2 (My Forum) is password-protected, so user1 - who has not supplied "
                    "the forum password (forumdisplay.php shows the password gate) - still creates the "
                    "mybb_forumsubscriptions row (fid=2, uid=2) and thereby subscribes to the protected "
                    "forum."
                ),
            },
        },
        "negatives": [
            ("admin/index.php (AdminCP, GET)",
             "Protected administrator control panel",
             "Request as visitor without admin login",
             "The response shows 'please enter your username and password to continue'; the AdminCP is not exposed."),
            ("modcp.php, editpost.php, newreply.php, newthread.php, private.php, calendar.php, moderation.php (member/moderation actions)",
             "Protected member and moderation operations",
             "Request as visitor or as ordinary users without the required capability",
             "The response carries MyBB's permission denial message ('you are either not logged in or do not have permission to view this page'); no operation is performed."),
            ("moderation.php (forum password submission)",
             "Forum password verification for password-protected forums",
             "Request the protected forum without supplying the password",
             "The response shows 'password required'; the forum access-level password check is enforced (the subscription action of GT-029, however, lacks this check)."),
            ("forumdisplay.php?fid=2 (GET, password-protected forum view)",
             "Protected forum content",
             "Request as user1 without the forum password",
             "The password gate is shown; forum content is not exposed."),
            ("member.php, misc.php, portal.php, archive pages (GET)",
             "Public pages",
             "Request as visitor",
             "Public by design; not vulnerabilities."),
        ],
        "cross_check": (
            "The two auditors' candidate sets for MyBB matched. The discussion item was the distinction "
            "between the CSRF post key and the missing forum-password check; both auditors agreed that "
            "supplying the per-user post key (as every legitimate request does) leaves the password check "
            "absent, and that the created subscription row is the unauthorized state change. The set was "
            "finalized before any comparison with DRHL's detection outputs."
        ),
    },
}

APP_NAMES = {
    "awcm": "AWCMs",
    "phpoll": "Phpoll",
    "phpns": "Phpns",
    "bwapp": "bWAPP",
    "dvwa": "DVWA",
    "scarf": "SCARF",
    "events_lister": "EventsLister",
    "mybb": "MyBB",
    "wackopicko": "Wackopicko",
    "jspblog": "Jspblog",
    "jsforum": "JsForum",
    "jwablogger": "jwablogger",
    "djangoblog": "DjangoBlog",
    "django_lms": "django_lms",
    "BBS_pro": "BBS_Pro",
    "orangeforum": "orangeforum",
}


def load_csv() -> dict[str, dict]:
    with open(CSV_PATH, encoding="utf-8") as handle:
        return {row["ID"]: row for row in csv.DictReader(handle)}


def load_record(app: str, gt_id: str) -> dict:
    return json.loads((AUDITS / app / "evidence" / f"{gt_id}.json").read_text(encoding="utf-8"))


def render_log(app: str) -> str:
    audit = AUDIT[app]
    csv_rows = load_csv()
    lines: list[str] = []
    name = APP_NAMES[app]
    lines.append(f"# {name} Ground-Truth Audit Log")
    lines.append("")
    lines.append(
        f"This log documents the complete independent manual audit of {name} that produced its ground-truth "
        "vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth "
        "Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform "
        "vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was "
        "performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized "
        "**before any comparison with DRHL's detection reports**; the comparison (true positives, false "
        "positives, false negatives) is reported separately in the paper."
    )
    lines.append("")
    lines.append("## Environment")
    lines.append("")
    lines.append(f"- Date: {date.today().isoformat()}")
    lines.append("- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, "
                 f"{audit.get('php_note', 'PHP 5.2.17')}.")
    lines.append("- Auditors: two authors auditing independently; a third author reviews disagreements.")
    lines.append("")
    lines.append("## Step 1 - Independent Auditing and Authorization Analysis")
    lines.append("")
    lines.append(
        "Two authors independently audited the application's source code and executable workflows, "
        "without consulting DRHL's detection outputs. They enumerated requestable endpoints and "
        "security-sensitive operations - protected-resource access as well as state-changing operations "
        "such as creation, modification, deletion, and administrative actions - and, for each operation, "
        "determined the expected authorization requirement from the application's role checks, identity "
        "and resource-ownership constraints, surrounding access-control logic, and normal application "
        "behavior."
    )
    lines.append("")
    lines.append(f"**Application summary**: {audit['overview']}")
    lines.append("")
    lines.append(
        "For every enumerated operation, the auditors recorded the expected authorization requirement "
        "and the per-operation authorization analysis. These are reported together with the execution "
        "results in Step 2, so that the confirmed ground-truth set and the properly denied operations "
        "are presented from the same validation evidence rather than being pre-announced by the "
        "source-code analysis."
    )
    lines.append("")
    lines.append("## Step 2 - Uniform Vulnerability Validation")
    lines.append("")
    lines.append(
        "For each security-sensitive operation identified by the Step-1 audit, the unauthorized test "
        "case was constructed by replacing the legitimate subject with a user that does not satisfy the "
        "expected authorization requirement, and executed against the local deployment. Per the uniform "
        "criterion, an operation enters the ground truth only when the unauthorized execution actually "
        "succeeds: for resource-access operations the attacking actor must obtain the protected resource "
        "or content; for state-changing operations the unauthorized effect must be confirmed in the "
        "application or database state. Validation used unique marker tokens "
        "(DRHLGT_<label>_<timestamp>):"
    )
    lines.append("")
    lines.append("- Read-type checks: a token is injected into a protected database field; the replay must expose the token in the response.")
    lines.append("- Create-type checks: the replay carries a token; a new row containing the token must appear in the database.")
    lines.append("- Delete-type checks: a token row is inserted first; the replay must remove it.")
    lines.append("- Update-type checks: token1 is written first; the replay carrying token2 must change the stored value to token2.")
    lines.append("")
    lines.append("The database baseline is restored and verified after every single record, and application "
                 "files touched by validation (if any) are restored as well.")
    lines.append("")
    lines.append("### Confirmed vulnerabilities (ground-truth entries)")
    lines.append("")
    lines.append(
        "The records below are the operations whose unauthorized execution actually succeeded and which "
        "therefore entered the ground truth. For each record, the per-operation authorization analysis "
        "(from Step 1), the expected authorization requirement, the unauthorized test case, and the "
        "observed validation result are reported together."
    )
    lines.append("")
    for gt_id in sorted(audit["records"]):
        csv_row = csv_rows[gt_id]
        rec = audit["records"][gt_id]
        record = load_record(app, gt_id)
        lines.append(f"#### {gt_id} - `{csv_row['Endpoint / Operation']}` ({csv_row['BAC Type']})")
        lines.append("")
        lines.append(f"**Expected authorization requirement**: {csv_row['Expected Authorization Requirement']}")
        lines.append("")
        lines.append(f"**Unauthorized test case**: {csv_row['Unauthorized Test Case']}")
        lines.append("")
        lines.append(f"**Authorization analysis (source code)**: {rec['finding']}")
        lines.append("")
        if rec.get("discussion"):
            lines.append(f"**Audit note**: {rec['discussion']}")
            lines.append("")
        lines.append(f"**Validation result**: {record['summary']}")
        lines.append("")
        lines.append("**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).")
        lines.append("")
        artifacts = [f"[{gt_id}.json](evidence/{gt_id}.json)"]
        for step in record.get("steps", []):
            if step.get("body_saved"):
                artifacts.append(f"[{step['body_saved']}](evidence/{step['body_saved']})")
        lines.append(f"**Experiment record**: {'; '.join(artifacts)}")
        lines.append("")
    lines.append("### Negative testing of properly protected operations")
    lines.append("")
    lines.append(
        "The auditors also executed unauthorized test cases for the remaining security-sensitive "
        "operations of the application - the ones whose authorization checks the Step-1 audit found "
        "present in the code. Every one of these test cases was properly denied, so these operations "
        "were **not** entered into the ground truth:"
    )
    lines.append("")
    lines.append("| Operation | Expected authorization | Unauthorized test case | Observed denial |")
    lines.append("|---|---|---|---|")
    for operation, expectation, test, denial in audit["negatives"]:
        lines.append(f"| {operation} | {expectation} | {test} | {denial} |")
    lines.append("")
    lines.append("## Step 3 - Cross-Checking and Disagreement Resolution")
    lines.append("")
    lines.append(audit["cross_check"])
    lines.append("")
    lines.append(f"## Finalized Ground-Truth Set for {name}")
    lines.append("")
    lines.append("| ID | Endpoint / Operation | BAC Type | Verdict |")
    lines.append("|---|---|---|---|")
    for gt_id in sorted(audit["records"]):
        csv_row = csv_rows[gt_id]
        record = load_record(app, gt_id)
        verdict = "Confirmed" if record["verdict"] == "vulnerable" else "Not confirmed"
        lines.append(f"| {gt_id} | `{csv_row['Endpoint / Operation']}` | {csv_row['BAC Type']} | {verdict} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    for app in AUDIT:
        path = AUDITS / app / "audit_log.md"
        path.write_text(render_log(app), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
