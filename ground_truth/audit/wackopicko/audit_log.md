# Wackopicko Ground-Truth Audit Log

This log documents the complete independent manual audit of Wackopicko that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17; the application is deployed at the web root (http://localhost/index.php).
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: Wackopicko authenticates through session login (users/login.php) and gates the user and picture pages with require_login(). The audit enumerated the user-profile and picture-download endpoints and checked whether object-level authorization (ownership or purchase entitlement) is enforced beyond the login requirement.

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

#### GT-030 - `users/view.php?userid=11` (HPE)

**Expected authorization requirement**: An ordinary user may view only their own protected profile unless explicitly authorized to view another account.

**Unauthorized test case**: Log in as user1 and change userid to user2's identifier 11.

**Authorization analysis (source code)**: users/view.php enforces only require_login(); it then loads the account selected by $_GET['userid'] and renders that user's login name and their picture list without any ownership or authorization check - any authenticated user can open any other user's profile page.

**Audit note**: Audit note: the endpoint text in the ground-truth table refers to the original deployment (user2's identifier 11); in the current deployment user id 11 is the seeded user 'bryce' (owner of pictures 22/23). Validation used the current deployment's data and this mapping is recorded in the evidence file.

**Validation result**: user1 GET users/view.php?userid=11 returned 200; the profile page of user id=11 was served and the token placed in that user's login field was exposed (exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-030.json](evidence/GT-030.json); [GT-030_gt030_user1_view_user11.html](evidence/GT-030_gt030_user1_view_user11.html)

#### GT-031 - `users/sample.php?userid=p1 (login-gate bypass of the profile view)` (VPE)

**Expected authorization requirement**: The user profile view (users/view.php) requires an authenticated login; the sample.php wrapper must not bypass this requirement - unauthenticated visitors must not be able to view a user's profile page.

**Unauthorized test case**: Request users/sample.php?userid=11 as visitor without a session.

**Authorization analysis (source code)**: users/sample.php sets $usercheck=False and includes view.php, deliberately bypassing the require_login() gate that the regular profile page (users/view.php) enforces: an unauthenticated visitor receives another user's profile page.

**Validation result**: visitor GET users/sample.php?userid=11 returned 200 and served the profile page of user id=11 with the token placed in the login field exposed (exposed=True); the regular entry users/view.php requires login and redirects the visitor (redirected=True); the instrumented login field was reverted afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-031.json](evidence/GT-031.json); [GT-031_gt031_visitor_sample.html](evidence/GT-031_gt031_visitor_sample.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| cart/action.php, cart/confirm.php, cart/review.php, comments/add_comment.php, comments/delete_preview_comment.php, comments/preview_comment.php, pictures/purchased.php, pictures/view.php, users/similar.php, users/view.php (GET/POST) | Protected cart, comment, picture, and profile operations | Request as visitor without a session | The requests are redirected (HTTP 302/303) to users/login.php; no operation is performed. |
| cart/add_coupon.php (GET) | Protected coupon administration | Request as visitor without a session | The unauthorized response body is empty; no coupon action is performed. |
| error.php (GET) | Public error page | Request as visitor | Public utility page by design; not a vulnerability. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for Wackopicko matched. The discussion item was the mapping of userid=11 to the current deployment (recorded in GT-030). Both auditors agreed that sample.php deliberately bypasses the require_login() gate of the profile view and that the visitor-rendered profile page is the unauthorized access. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for Wackopicko

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-030 | `users/view.php?userid=11` | HPE | Confirmed |
| GT-031 | `users/sample.php?userid=p1 (login-gate bypass of the profile view)` | VPE | Confirmed |
