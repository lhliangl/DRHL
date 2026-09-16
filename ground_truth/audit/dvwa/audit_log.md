# DVWA Ground-Truth Audit Log

This log documents the complete independent manual audit of DVWA that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.4.45 (the DVWA source requires PHP >= 5.4; the deployment was switched to 5.4.45 for this application).
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: DVWA declares the required capabilities of each page through dvwaPageStartup(); pages that declare the authenticated lab role redirect unauthenticated visitors to login.php. The audit enumerated the pages reachable without a session - in particular the pages that declare no required capability - and the database setup entry point.

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

#### GT-021 - `about.php` (VPE)

**Expected authorization requirement**: The page must require the authenticated security-lab role assumed by the application workflow.

**Unauthorized test case**: Request about.php as visitor without a DVWA session.

**Authorization analysis (source code)**: about.php calls dvwaPageStartup( array() ) with an empty capability list, so the About page is served without any session; the lab workflow, however, assumes the authenticated security-lab role for its content pages.

**Validation result**: visitor GET about.php returned 200 and serves the DVWA About page content without any session (about_content_exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-021.json](evidence/GT-021.json); [GT-021_gt021_visitor_about.html](evidence/GT-021_gt021_visitor_about.html)

#### GT-022 - `instructions.php?doc=p1` (VPE)

**Expected authorization requirement**: The requested instruction document must require the authenticated security-lab role assumed by the application workflow.

**Unauthorized test case**: Request instructions.php with a valid doc value as visitor without a DVWA session.

**Authorization analysis (source code)**: instructions.php also calls dvwaPageStartup( array() ) with no required capability; a visitor retrieves the rendered instruction documents (README and the other bundled docs) without any session.

**Validation result**: visitor GET instructions.php?doc=readme returned 200 and serves the protected instruction document (document_content_exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-022.json](evidence/GT-022.json); [GT-022_gt022_visitor_instructions.html](evidence/GT-022_gt022_visitor_instructions.html)

#### GT-023 - `setup.php` (VPE)

**Expected authorization requirement**: Only an administrator may initialize or reset the DVWA database.

**Unauthorized test case**: Request and invoke setup.php as visitor without a DVWA session.

**Authorization analysis (source code)**: setup.php exposes the Create/Reset Database action to unauthenticated visitors. The action is guarded only by an anti-CSRF token (checkToken against the session token); CSRF protection is not authorization - the visitor obtains the token from the form itself (the form carries the token of the visitor's own session) and executes the full database reset: the database is dropped and recreated and the default user accounts are reseeded.

**Audit note**: The auditors discussed the anti-CSRF token: supplying the form's own user_token reproduces the ordinary browser flow and does not require any privilege, so the token does not mitigate the missing authorization check. Both auditors agreed that the visitor-triggered database reset is the unauthorized state change.

**Validation result**: visitor GET setup.php returned 200 with the Create/Reset Database form (exposed=True); the visitor-triggered reset rebuilt the database: marker row 1->0, users 5->5; baseline restored afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-023.json](evidence/GT-023.json); [GT-023_gt023_visitor_setup.html](evidence/GT-023_gt023_visitor_setup.html); [GT-023_gt023_visitor_setup_action.html](evidence/GT-023_gt023_visitor_setup_action.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| index.php, security.php (GET) | Protected lab pages (authenticated security-lab role) | Request as visitor without a DVWA session | The requests are redirected (HTTP 302) to login.php; no lab content is exposed. |
| vulnerabilities/* module pages (brute, captcha, csp, csrf, exec, fi, javascript, open_redirect, sqli, sqli_blind, upload, weak_id, xss_d, xss_r, xss_s, cryptography, api; GET) | Protected challenge/lab module pages (authenticated security-lab role) | Request as visitor without a DVWA session | The requests are redirected (HTTP 302) to login.php; the lab modules are not exposed. |
| vulnerabilities/authbypass/* pages (GET) | Protected authentication-bypass challenge pages | Request as visitor without a DVWA session | The responses carry the 'access denied' marker; the challenge content is not exposed. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for DVWA matched. The discussion item was the anti-CSRF token of GT-023 (recorded above); both auditors agreed that the token is session-bound CSRF protection and not an authorization check, and that the confirmed database reset is the unauthorized state change. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for DVWA

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-021 | `about.php` | VPE | Confirmed |
| GT-022 | `instructions.php?doc=p1` | VPE | Confirmed |
| GT-023 | `setup.php` | VPE | Confirmed |
