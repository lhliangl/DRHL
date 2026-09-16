# AWCMs Ground-Truth Audit Log

This log documents the complete independent manual audit of AWCMs that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: AWCMs is a legacy PHP content-management application. Authentication is established in header.php: a member id is taken from the session (`$_SESSION['awcm_member']`) or, as a fallback, from the `awcm_member` cookie (member id + 197), which header.php accepts after only checking that the id exists in awcm_members - no password is verified. The audit enumerated the member-facing pages and the control-panel endpoints and checked each for authentication and authorization gates.

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

#### GT-001 - `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1` (VPE)

**Expected authorization requirement**: Only an authenticated member may open the member avatar control.

**Unauthorized test case**: Request m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500 as a visitor without an authenticated member session.

**Authorization analysis (source code)**: m_cp_avatar.php renders the member avatar control (the update form plus the avatar iframe) without an authentication gate. Consequently, a visitor can request the normalized endpoint `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1` and obtain the member-only avatar form.

**Audit note**: The ground-truth record is defined at the normalized GET endpoint. The retained replay uses the concrete values height=400 and width=500 and confirms that the member-only avatar form is exposed to an unauthenticated visitor.

**Validation result**: visitor GET returned 200 with the avatar update form (form_present=True); plain visitor POST got 200 and did not modify DB rows (sessionless $member binds to id 'no'); with a forged awcm_member cookie the POST updated admin avatar 'DRHLGT_avatar_before_8670635114' -> 'DRHLGT_avatar_after_8670635114' without any password.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-001.json](evidence/GT-001.json); [GT-001_gt001_visitor_get.html](evidence/GT-001_gt001_visitor_get.html)

#### GT-002 - `member.php?id=1 (administrator profile)` (VPE)

**Expected authorization requirement**: An ordinary member must not obtain administrator-only profile information when the selected id identifies the administrator.

**Unauthorized test case**: Log in as user1 and request member.php?id=1.

**Authorization analysis (source code)**: member.php takes `$_GET['id']` and renders the profile fields (username, country, sex, title, signature) through f_find_member() without checking whether the viewer is the profile owner or an administrator. Requesting id=1 returns the administrator's profile data to any authenticated member.

**Validation result**: vertical: user1 reads admin profile: logged in as user1, requested member.php?id=1; response status 200, token DRHLGT_profile_8670638955 from member id=1 title exposed=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-002.json](evidence/GT-002.json); [GT-002_GT-002_user1.html](evidence/GT-002_GT-002_user1.html)

#### GT-003 - `member.php?id=3 (another member profile)` (HPE)

**Expected authorization requirement**: A member may view only profile data permitted by the application and must not obtain another member's protected profile by changing id.

**Unauthorized test case**: Log in as user1 and replace the profile id with the database id of user2.

**Authorization analysis (source code)**: Same defect as GT-002 for ordinary members: member.php?id=3 returns user2's profile fields to user1 with no ownership or administrative check.

**Validation result**: horizontal: user1 reads user2 profile: logged in as user1, requested member.php?id=3; response status 200, token DRHLGT_profile_8670642616 from member id=3 signature exposed=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-003.json](evidence/GT-003.json); [GT-003_GT-003_user1.html](evidence/GT-003_GT-003_user1.html)

#### GT-004 - `install/index.php` (VPE)

**Expected authorization requirement**: The installation interface must be unavailable after deployment or restricted to an administrator.

**Unauthorized test case**: Request install/index.php as visitor.

**Authorization analysis (source code)**: install/index.php renders the installation entry (language selection) and proceeds to install/step1.php with no post-deployment guard or authorization check; the installer remains invocable after the application has been deployed.

**Validation result**: visitor GET install/index.php returned 200 with the language-selection installer form (installer_form_present=True); the flow advances to step1.php (status 200).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-004.json](evidence/GT-004.json); [GT-004_gt004_visitor_install.html](evidence/GT-004_gt004_visitor_install.html)

#### GT-005 - `control/db_backup.php` (VPE)

**Expected authorization requirement**: Only an administrator may invoke database backup and receive the SQL dump.

**Unauthorized test case**: Request control/db_backup.php as visitor without control-panel authentication.

**Authorization analysis (source code)**: control/db_backup.php implements mysql_dump() over every table of the application database and returns the full SQL dump as an attachment. The endpoint enforces no control-panel authentication, so the entire database content is downloadable by an unauthenticated visitor.

**Validation result**: visitor GET control/db_backup.php returned 200 SQL attachment ('attachment; filename="backup_06/09/2026.sql"'); dump exposes the instrumented row token=True, contains 38 INSERT statements and includes awcm_control data=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-005.json](evidence/GT-005.json); [GT-005_gt005_visitor_dbdump.html](evidence/GT-005_gt005_visitor_dbdump.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| member_cp.php (GET) | Protected member-control-panel access | Request as visitor without a member session | The response performs a client-side redirect to index.php and renders the login form; the control panel is not exposed. |
| member_cp_pm.php (GET) | Protected private-message management access | Request as visitor without a member session | The response renders the login form; the private-message interface is not exposed. |
| send_lesson.php / send_news.php / send_pro.php / send_topic.php (GET, POST) | Protected article/news/lesson/program creation | Request as visitor without a member session | The response executes a client-side denial (history.back()) and renders the login form; no content is published. |
| send_flash.php / send_image.php / send_video.php (GET, POST) | Protected administrator content publication | Request as visitor without an administrator session | The response executes a client-side denial (history.back()); no content is published. |
| control/security.php (GET) | Control-panel security management | Request as visitor without control-panel authentication | The unauthorized response body is empty; no control-panel content is exposed. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for AWCMs matched after joint re-inspection. The discussion items recorded above (notably the normalized endpoint of GT-001) were resolved by joint re-reading of header.php and m_cp_avatar.php; no case required third-author escalation. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for AWCMs

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-001 | `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1` | VPE | Confirmed |
| GT-002 | `member.php?id=1 (administrator profile)` | VPE | Confirmed |
| GT-003 | `member.php?id=3 (another member profile)` | HPE | Confirmed |
| GT-004 | `install/index.php` | VPE | Confirmed |
| GT-005 | `control/db_backup.php` | VPE | Confirmed |
