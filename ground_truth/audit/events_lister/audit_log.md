# EventsLister Ground-Truth Audit Log

This log documents the complete independent manual audit of EventsLister that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: EventsLister has an admin directory whose pages are expected to be reachable only after admin login. The audit checked every admin page for an authentication gate.

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

#### GT-027 - `admin/setup.php` (VPE)

**Expected authorization requirement**: Only an administrator may execute database or administrator-account setup.

**Unauthorized test case**: Request and submit admin/setup.php as visitor.

**Authorization analysis (source code)**: admin/setup.php executes the database setup (event/no-events/admin table creation, no-events message, administrator-account insert with the submitted credentials, and the optional test event) with no authentication check. Validation used the fresh-install precondition (admin row cleared for the test) because the setup INSERT hard-codes id=1 and silently fails when that row already exists.

**Validation result**: visitor POST admin/setup.php returned 200; visitor recreated the administrator account id=1 with attacker-chosen email (created=True) and the setup inserted a Test Event row (events 21->22); baseline restored afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-027.json](evidence/GT-027.json); [GT-027_gt027_visitor_setup.html](evidence/GT-027_gt027_visitor_setup.html)

#### GT-028 - `admin/user_add.php` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may create another administrator account.

**Unauthorized test case**: Submit a new account through admin/user_add.php as visitor.

**Authorization analysis (source code)**: admin/user_add.php inserts the submitted account into the admin table with no authentication check; a visitor creates a new administrator account.

**Validation result**: visitor POST admin/user_add.php returned 200; a new administrator account row (id=4, uname=DRHLGT_addadmin_8670685443@example.test) was created without any login (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-028.json](evidence/GT-028.json); [GT-028_gt028_visitor_user_add.html](evidence/GT-028_gt028_visitor_user_add.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| admin/index.php, admin/list.php, admin/users.php (GET) | Protected admin overview/listing pages | Request as visitor without admin login | The requests are redirected (HTTP 302) to admin/login.php; no admin content is exposed. |
| admin/add.php, admin/copy.php, admin/delete.php, admin/message.php, admin/update.php, admin/user_delete.php (POST) | Protected event/user administration actions | Submit as visitor without admin login | The requests are redirected (HTTP 302) to admin/login.php; no state change is performed. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for EventsLister matched. The discussion item was GT-027's hard-coded id=1 INSERT, which required the documented fresh-install precondition; both auditors agreed the missing authentication gate is the vulnerability regardless of that precondition. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for EventsLister

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-027 | `admin/setup.php` | VPE | Confirmed |
| GT-028 | `admin/user_add.php` | VPE | Confirmed |
