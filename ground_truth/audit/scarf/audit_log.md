# SCARF Ground-Truth Audit Log

This log documents the complete independent manual audit of SCARF that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: SCARF uses session-based login with helper functions (require_admin(), require_loggedin()) for protected branches. The audit checked every administrative entry point and every branch of the management pages against these helpers.

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

#### GT-024 - `install.php` (VPE)

**Expected authorization requirement**: The installer must be disabled after deployment or restricted to an administrator.

**Unauthorized test case**: Request install.php as visitor.

**Authorization analysis (source code)**: install.php renders the installer form and, on submission, drops and recreates the scarf database (confirmdrop flow), creates the tables, reseeds the default options, and rewrites config.php - all with no authentication check. A visitor can trigger a complete reinstallation of the deployed application.

**Validation result**: visitor GET install.php returned 200 with the installer form (form_exposed=True); visitor-triggered install dropped and recreated the scarf database: marker 1->0, fresh default options=1; config.php and database were restored afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-024.json](evidence/GT-024.json); [GT-024_gt024_visitor_install.html](evidence/GT-024_gt024_visitor_install.html); [GT-024_gt024_visitor_install_confirm.html](evidence/GT-024_gt024_visitor_install_confirm.html); [GT-024_gt024_visitor_install_done.html](evidence/GT-024_gt024_visitor_install_done.html)

#### GT-025 - `comments.php` (VPE)

**Expected authorization requirement**: Only the administrator may open the comment-moderation page and view pending comments.

**Unauthorized test case**: Request comments.php as visitor and as ordinary users.

**Authorization analysis (source code)**: comments.php without the comment_id parameter renders the moderation list of all pending comments (approved=0). Only the single-comment branch (comment_id set) calls require_admin(); the pending-comment moderation list itself is rendered to visitors and ordinary users.

**Validation result**: pending comment token exposed to visitor=True, user1=True, user2=True on GET comments.php.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-025.json](evidence/GT-025.json); [GT-025_gt025_visitor_comments.html](evidence/GT-025_gt025_visitor_comments.html); [GT-025_gt025_user1_comments.html](evidence/GT-025_gt025_user1_comments.html); [GT-025_gt025_user2_comments.html](evidence/GT-025_gt025_user2_comments.html)

#### GT-026 - `generaloptions.php` (VPE)

**Expected authorization requirement**: Only the administrator may change global conference options.

**Unauthorized test case**: Submit the general-options form as visitor or an ordinary user.

**Authorization analysis (source code)**: generaloptions.php applies the submitted POST fields directly as 'UPDATE options SET value=... WHERE name=...' (and writes uploaded files to the configured paths) without any administrator check. A visitor can rewrite any global conference option.

**Validation result**: visitor POST generaloptions.php returned 200; global option 'Conference Name' changed DRHLGT_conf_before_8670682765 -> DRHLGT_conf_after_8670682765 (updated=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-026.json](evidence/GT-026.json)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| addsession.php, editpaper.php, editsession.php (state-changing POST) | Protected session/paper management | Submit as visitor without a session | The response carries the denial text "you don't have access to view this page"; no state change is performed. |
| useroptions.php (POST) | Protected account-options change | Submit as visitor without a session | The response carries the denial text "you must be logged in to access this feature"; no change is performed. |
| comments.php comment submission branch (POST) | Protected comment submission (requires login) | Submit as visitor without a session | The submission branch calls require_loggedin() and is denied; the moderation-list branch (GT-025) is the confirmed vulnerability. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for SCARF matched. The discussion item was GT-024's side effects (database drop/recreate and the config.php rewrite), which were handled by backing up config.php and restoring the database baseline after validation. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for SCARF

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-024 | `install.php` | VPE | Confirmed |
| GT-025 | `comments.php` | VPE | Confirmed |
| GT-026 | `generaloptions.php` | VPE | Confirmed |
