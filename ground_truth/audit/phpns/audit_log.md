# Phpns Ground-Truth Audit Log

This log documents the complete independent manual audit of Phpns that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: Phpns assigns rank permission strings to user ranks; inc/auth.php exposes them as string offsets ($globalvars['rank'][N]). The audit checked, for every state-changing or management endpoint, whether the rank-level capability check is accompanied by an object-level authorization check (ownership or administrator override).

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

#### GT-009 - `install/index.php` (VPE)

**Expected authorization requirement**: The installer must be disabled after deployment or restricted to an authenticated administrator.

**Unauthorized test case**: Request install/index.php without a privileged session.

**Authorization analysis (source code)**: install/index.php serves the installation wizard (license step, then the database configuration step) to unauthenticated visitors; no guard disables the installer after deployment.

**Validation result**: visitor GET install/index.php returned 200 with the installer database-configuration form (installer_db_form_present=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-009.json](evidence/GT-009.json); [GT-009_gt009_visitor_install.html](evidence/GT-009_gt009_visitor_install.html)

#### GT-010 - `article.php?do=comments&id=6` (VPE)

**Expected authorization requirement**: Only a user with the article-edit or comment-moderation privilege may view the comment-management interface for article 6.

**Unauthorized test case**: Log in with the register account and request the comment-management page for article 6.

**Authorization analysis (source code)**: article.php `do=comments` renders the comment-management interface for article 6 and lists its comments without any permission check at all (unlike `do=edit`, which checks the rank's edit-article capability). The low-privilege register account opens the moderation interface for an article it does not own.

**Validation result**: register GET article.php?do=comments&id=6 returned 200; comment moderation list exposes instrumented comment token=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-010.json](evidence/GT-010.json); [GT-010_gt010_register_comments.html](evidence/GT-010_gt010_register_comments.html)

#### GT-011 - `article.php?action=delete&do=comments&id=6` (VPE)

**Expected authorization requirement**: Only a user with the article-edit or comment-moderation privilege may delete comments of article 6.

**Unauthorized test case**: Log in with the register account and submit selected comment identifiers to the delete operation.

**Authorization analysis (source code)**: The same `do=comments` branch processes `action=delete` using the POST keys as comment ids (`DELETE FROM comments WHERE id IN (...)`), again with no permission check. The low-privilege register account deletes comments of article 6.

**Validation result**: register POST article.php?action=delete&do=comments&id=6 returned 200; instrumented comment id=24 of article 6 was deleted (exists_after=0).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-011.json](evidence/GT-011.json)

#### GT-012 - `article.php?do=edit&id=6` (HPE)

**Expected authorization requirement**: Only the article author or an administrator may open the edit interface for article 6.

**Unauthorized test case**: Log in as user1 and replace the article id with an article owned by user2.

**Authorization analysis (source code)**: article.php `do=edit` checks only the rank-level edit-article capability ($globalvars['rank'][14]) and loads the article row by `$_GET['id']` without verifying that the current user is the article author or an administrator. user1 opens the edit form of user2's article 6.

**Validation result**: user1 GET article.php?do=edit&id=6 returned 200; user2's article text token exposed in the edit form=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-012.json](evidence/GT-012.json); [GT-012_gt012_user1_edit_article6.html](evidence/GT-012_gt012_user1_edit_article6.html)

#### GT-013 - `article.php?do=editp (submit update for id=6)` (HPE)

**Expected authorization requirement**: Only the article author or an administrator may update article 6.

**Unauthorized test case**: Log in as user1 and submit the article-edit payload with id=6 owned by user2.

**Authorization analysis (source code)**: article.php `do=editp` applies the same rank-level check and updates the article row selected by the POST id; edit_item() also overwrites article_author with the current session user, so user1 not only modifies user2's article but takes ownership of it.

**Validation result**: user1 POST article.php?do=editp returned 200; article 6 article_text changed DRHLGT_art_before_8670667825 -> DRHLGT_art_after_8670667825 (updated=True) and article_author became 'user1'.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-013.json](evidence/GT-013.json)

#### GT-014 - `user.php?do=edit&id=6` (HPE)

**Expected authorization requirement**: A user may open only their own account-edit interface unless the current user is an administrator.

**Unauthorized test case**: Log in as user1 and replace id with user2's account id.

**Authorization analysis (source code)**: user.php `do=edit` checks only the rank-level edit-users capability ($globalvars['rank'][20]) and loads the target account by `$_GET['id']` without a self/owner constraint: a user may open the account-edit interface of another account whenever their rank permits editing users at all.

**Audit note**: Audit note: the endpoint text in the ground-truth table says id=6, which refers to the original deployment; in the current deployment user2's account id is 11. Validation was performed against the current id (11) and this mapping is recorded in the evidence file.

**Validation result**: user1 GET user.php?do=edit&id=11 returned 200; user2's account data token exposed in the edit form=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-014.json](evidence/GT-014.json); [GT-014_gt014_user1_edit_user11.html](evidence/GT-014_gt014_user1_edit_user11.html)

#### GT-015 - `user.php?do=editp (submit update for id=6)` (HPE)

**Expected authorization requirement**: A user may modify only their own account unless the current user is an administrator.

**Unauthorized test case**: Log in as user1 and submit the account-edit payload for user2's id.

**Authorization analysis (source code)**: user.php `do=editp` applies the same rank-level check and updates the account row selected by the POST id (user_name, full_name, email, rank_id, etc.) without a self/owner constraint; user1 modifies user2's account data.

**Validation result**: user1 POST user.php?do=editp returned 200; user2 (id=11) full_name changed DRHLGT_usr_before_8670670466 -> DRHLGT_usr_after_8670670466 (updated=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-015.json](evidence/GT-015.json)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| preferences.php (management actions), user.php (rank/login-record management), article.php (other management actions), manage.php (user-management actions) | Protected administrator/management operations | Request as the low-privilege register account or as ordinary users | The request is redirected (HTTP 302) to index.php?do=permissiondenied; the rank-level permission checks are enforced and no management content is exposed. |
| user.php / manage.php / article.php (ordinary member actions within their own rank capabilities) | Rank-permitted member actions | Request as an ordinary authenticated user within the rank's capabilities | Access succeeds for operations the rank is permitted to perform; these operations carry no additional authorization requirement and are not vulnerabilities. |
| install/install.inc.php, install/install.tmp.php (GET) | Installer helper files | Request as visitor | Standalone helper fragments without sensitive actions; not counted as vulnerabilities. |
| install/upgrade.php (GET) | Installer upgrade entry | Request as visitor | The request is redirected away; the upgrade entry does not expose a usable action to a visitor. |
| index.php, help.php (GET) | Public pages | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for Phpns matched. The discussion items were: (a) the string-offset semantics of the rank permissions (resolved by tracing inc/auth.php and the login session), and (b) the id mapping for GT-014 between the original deployment and the current one (resolved by identifying user2's current account id in the database). The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for Phpns

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-009 | `install/index.php` | VPE | Confirmed |
| GT-010 | `article.php?do=comments&id=6` | VPE | Confirmed |
| GT-011 | `article.php?action=delete&do=comments&id=6` | VPE | Confirmed |
| GT-012 | `article.php?do=edit&id=6` | HPE | Confirmed |
| GT-013 | `article.php?do=editp (submit update for id=6)` | HPE | Confirmed |
| GT-014 | `user.php?do=edit&id=6` | HPE | Confirmed |
| GT-015 | `user.php?do=editp (submit update for id=6)` | HPE | Confirmed |
