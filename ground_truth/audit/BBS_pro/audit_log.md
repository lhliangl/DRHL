# BBS_Pro Ground-Truth Audit Log

This log documents the complete independent manual audit of BBS_Pro that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Python 2.7 Django development server (http://127.0.0.1:8000/), SQLite database.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: BBS_Pro is a Python 2 Django bulletin-board application. The audit enumerated the bulletin management endpoints (bbs_pub, bbs_sub, sub_comment, and the login/logout flow) and checked whether the publication page enforces the staff-only policy applied elsewhere in the application.

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

#### GT-048 - `bbs_pub/` (VPE)

**Expected authorization requirement**: The bulletin-publication page is an authenticated-user feature: logged-in users may open it, but unauthenticated visitors must be redirected to the login page.

**Unauthorized test case**: Request bbs_pub/ as visitor without a session.

**Authorization analysis (source code)**: The original bbs_pub view renders the bulletin-publication form without any login check: unauthenticated visitors receive the full publication form. The submission endpoint (bbs_sub/) resolves the author from request.user, which is anonymous for a visitor, so the anonymous submission attempt terminates with HTTP 500 and creates no post; the confirmed violation is therefore the page-level exposure of the authenticated-user publication form. Logged-in users opening the page is by design.

**Audit note**: Audit note: the deployment is kept in its original state (the view carries no login check). For the validation, user1's password was reset through the application's own User.set_password mechanism and a category name was instrumented with a marker token; both were reverted afterwards. Both auditors agreed that the visitor-rendered publication form is the violation, with the failed anonymous submission recorded as its boundary.

**Validation result**: visitor GET /bbs_pub/ returned 200 and served the bulletin-publication form (category token exposed=True); the anonymous submission attempt crashed with HTTP 500 and created no post (posts 16 -> 16); a logged-in ordinary user opens the page by design (200). The category name was reverted afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-048.json](evidence/GT-048.json); [GT-048_gt048_visitor_bbs_pub.html](evidence/GT-048_gt048_visitor_bbs_pub.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| bbs_sub/, sub_comment/ (state-changing submissions) | Protected bulletin/comment submission | Submit as visitor without a session | The requests terminate with HTTP 500 before any state change; no bulletin or comment is created. |
| acc_login (login flow) | Authentication entry | Submit wrong credentials | The login page shows the 'Wrong username or password.' error and no session is established. |
| logout/, home (public pages) | Public pages | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for BBS_Pro matched. The discussion item was the authorization policy of bbs_pub (recorded in GT-048); both auditors agreed that the original view applies no login check to the bulletin-publication page and that the visitor-rendered publication form is the violation (the anonymous submission attempt fails and creates nothing, recorded as the boundary). The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for BBS_Pro

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-048 | `bbs_pub/` | VPE | Confirmed |
