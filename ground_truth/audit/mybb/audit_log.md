# MyBB Ground-Truth Audit Log

This log documents the complete independent manual audit of MyBB that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: MyBB's usercp2.php verifies the per-user post key (CSRF protection) for every request and then dispatches the action. The audit checked whether the subscription action additionally enforces the forum-level access constraints, in particular the forum password, and re-tested the standard member/admin endpoints for baseline behavior.

For every enumerated operation, the auditors recorded the expected authorization requirement and the per-operation authorization analysis. These are reported together with the execution results in Step 2, so that the confirmed ground-truth set and the properly denied operations are presented from the same validation evidence rather than being pre-announced by the source-code analysis.

## Step 2 - Uniform Vulnerability Validation

For each security-sensitive operation identified by the Step-1 audit, the unauthorized test case was constructed by replacing the legitimate subject with a user that does not satisfy the expected authorization requirement, and executed against the local deployment. Per the uniform criterion, an operation enters the ground truth only when the unauthorized execution actually succeeds: for resource-access operations the attacking actor must obtain the protected resource or content; for state-changing operations the unauthorized effect must be confirmed in the application or database state. Validation used unique marker tokens (DRHLGT_<label>_<timestamp>):

- Read-type checks: a token is injected into a protected database field; the replay must expose the token in the response.
- Create-type checks: the replay carries a token; a new row containing the token must appear in the database.
- Delete-type checks: a token row is inserted first; the replay must remove it.
- Update-type checks: token1 is written first; the replay carrying token2 must change the stored value to token2.

The database baseline is restored and verified after every single record, and application files touched by validation (if any) are restored as well.

### Confirmed vulnerabilities (ground-truth entries)

The records below are the operations whose unauthorized execution actually succeeded and which therefore entered the ground truth. For each record, the per-operation authorization analysis (from Step 1), the expected authorization requirement, the unauthorized test case, and the observed validation result are reported together.

#### GT-029 - `usercp2.php?action=addsubscription&fid=p1&type=forum` (VPE)

**Expected authorization requirement**: A logged-in user must supply the protected forum password before subscribing to a password-protected forum.

**Unauthorized test case**: Log in as an ordinary user who has not supplied the forum password and request the addsubscription action for that forum id.

**Authorization analysis (source code)**: usercp2.php?action=addsubscription&fid=2&type=forum runs verify_post_check() (the my_post_key is CSRF protection, not authorization) and then checks only the forum view permissions before calling add_subscribed_forum(). The forum password is never verified. Forum 2 (My Forum) is password-protected, so user1 - who has not supplied the forum password (forumdisplay.php shows the password gate) - still creates the mybb_forumsubscriptions row (fid=2, uid=2) and thereby subscribes to the protected forum.

**Validation result**: forum 2 is password-protected (forumdisplay shows password gate=True); user1 GET addsubscription returned 200 and created the subscription row [['2', '2']] without ever supplying the forum password (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-029.json](evidence/GT-029.json); [GT-029_gt029_user1_forumdisplay.html](evidence/GT-029_gt029_user1_forumdisplay.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| admin/index.php (AdminCP, GET) | Protected administrator control panel | Request as visitor without admin login | The response shows 'please enter your username and password to continue'; the AdminCP is not exposed. |
| modcp.php, editpost.php, newreply.php, newthread.php, private.php, calendar.php, moderation.php (member/moderation actions) | Protected member and moderation operations | Request as visitor or as ordinary users without the required capability | The response carries MyBB's permission denial message ('you are either not logged in or do not have permission to view this page'); no operation is performed. |
| moderation.php (forum password submission) | Forum password verification for password-protected forums | Request the protected forum without supplying the password | The response shows 'password required'; the forum access-level password check is enforced (the subscription action of GT-029, however, lacks this check). |
| forumdisplay.php?fid=2 (GET, password-protected forum view) | Protected forum content | Request as user1 without the forum password | The password gate is shown; forum content is not exposed. |
| member.php, misc.php, portal.php, archive pages (GET) | Public pages | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for MyBB matched. The discussion item was the distinction between the CSRF post key and the missing forum-password check; both auditors agreed that supplying the per-user post key (as every legitimate request does) leaves the password check absent, and that the created subscription row is the unauthorized state change. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for MyBB

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-029 | `usercp2.php?action=addsubscription&fid=p1&type=forum` | VPE | Confirmed |
