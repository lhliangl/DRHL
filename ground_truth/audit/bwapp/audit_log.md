# bWAPP Ground-Truth Audit Log

This log documents the complete independent manual audit of bWAPP that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: bWAPP is an intentionally vulnerable application. The audit enumerated the standalone PHP pages reachable without a session and checked which of them expose privileged diagnostics, installation, or secret content to an unauthenticated visitor, and which state-changing actions enforce the login session.

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

#### GT-016 - `backdoor.php` (VPE)

**Expected authorization requirement**: The backdoor or privileged diagnostic page must not be accessible to an unauthenticated visitor.

**Unauthorized test case**: Request backdoor.php as visitor.

**Authorization analysis (source code)**: backdoor.php renders the 'NSA file uploader' form to unauthenticated visitors. The upload POST branch does check the login session, so the confirmed vulnerability is the exposure of the privileged diagnostic/backdoor page itself to a visitor.

**Validation result**: visitor GET backdoor.php returned 200 and exposes the NSA file uploader form (exposed=True); the upload action itself redirects a sessionless visitor to login.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-016.json](evidence/GT-016.json); [GT-016_gt016_visitor_backdoor.html](evidence/GT-016_gt016_visitor_backdoor.html)

#### GT-017 - `install.php` (VPE)

**Expected authorization requirement**: The installer must be disabled after deployment or restricted to an administrator.

**Unauthorized test case**: Request install.php as visitor.

**Authorization analysis (source code)**: install.php exposes the installer link and, when the database does not exist, the full database-creation flow (database, users table with default accounts, and the remaining tables) with no authorization check. Validation used a fresh-install precondition (database dropped for the test) because the installer refuses to reinstall over an existing database; the database was restored afterwards.

**Validation result**: visitor GET install.php returned 200 with the installer link (installer_link_exposed=True); the install action was invoked as visitor and completed (installed=True); database restored afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-017.json](evidence/GT-017.json); [GT-017_gt017_visitor_install_page.html](evidence/GT-017_gt017_visitor_install_page.html); [GT-017_gt017_visitor_install_action.html](evidence/GT-017_gt017_visitor_install_action.html)

#### GT-018 - `secret-cors-1.php` (VPE)

**Expected authorization requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.

**Unauthorized test case**: Request secret-cors-1.php as visitor without authorization.

**Authorization analysis (source code)**: secret-cors-1.php serves the hard-coded secret text with 'Access-Control-Allow-Origin: *' and no authorization check; the secret is returned verbatim to an unauthenticated visitor.

**Validation result**: visitor GET secret-cors-1.php returned 200; protected secret obtained without authorization=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-018.json](evidence/GT-018.json); [GT-018_GT-018_visitor.html](evidence/GT-018_GT-018_visitor.html)

#### GT-019 - `secret-cors-2.php` (VPE)

**Expected authorization requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.

**Unauthorized test case**: Request secret-cors-2.php as visitor without authorization.

**Authorization analysis (source code)**: secret-cors-2.php gates the secret on the HTTP Origin header. The header is client-supplied and trivially spoofable, so an unauthenticated visitor obtains the secret by sending 'Origin: http://intranet.itsecgames.com'. The auditors confirmed that the plain request (no Origin) returns the non-secret page, ruling out an unconditionally public page.

**Validation result**: visitor GET secret-cors-2.php returned 200; protected secret obtained without authorization=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-019.json](evidence/GT-019.json); [GT-019_GT-019_visitor.html](evidence/GT-019_GT-019_visitor.html); [GT-019_GT-019_visitor_headers.html](evidence/GT-019_GT-019_visitor_headers.html)

#### GT-020 - `secret-cors-3.php` (VPE)

**Expected authorization requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.

**Unauthorized test case**: Request secret-cors-3.php as visitor without authorization.

**Authorization analysis (source code)**: secret-cors-3.php serves the hard-coded secret text with no authorization or origin check; the secret is returned verbatim to an unauthenticated visitor.

**Validation result**: visitor GET secret-cors-3.php returned 200; protected secret obtained without authorization=True.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-020.json](evidence/GT-020.json); [GT-020_GT-020_visitor.html](evidence/GT-020_GT-020_visitor.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| credits.php, password_change.php, portal.php, reset.php, user_extra.php (state-changing POST) | Protected account/portal state changes | Submit the forms as visitor without a bWAPP session | The requests are redirected (HTTP 302) to login.php; no state change is performed. |
| top_security.php (GET) | Protected 'top security' page | Request as visitor | The response carries the denial text 'you are not welcome here'; the page content is not exposed. |
| test.php (GET) | Diagnostic test page | Request as visitor | The unauthorized response body is empty; nothing is exposed. |
| security_level_set.php (POST) | Security-level switch (lab convenience utility) | Request as visitor | Public utility page by design; not a vulnerability. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for bWAPP matched. The discussion item was GT-019, where the auditors verified that the secret is not exposed without the spoofed Origin header (otherwise the page would be unconditionally public); both agreed the spoofable trusted-origin check is the vulnerability. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for bWAPP

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-016 | `backdoor.php` | VPE | Confirmed |
| GT-017 | `install.php` | VPE | Confirmed |
| GT-018 | `secret-cors-1.php` | VPE | Confirmed |
| GT-019 | `secret-cors-2.php` | VPE | Confirmed |
| GT-020 | `secret-cors-3.php` | VPE | Confirmed |
