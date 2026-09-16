# django_lms Ground-Truth Audit Log

This log documents the complete independent manual audit of django_lms that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Django 2.x development server (http://localhost:8000/), PostgreSQL 14.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: django_lms guards its management views with @login_required and role decorators (for example, edit_post requires @login_required and @lecturer_required). The audit enumerated the item/event management endpoints and checked each for the same decorators.

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

#### GT-047 - `add_item/` (VPE)

**Expected authorization requirement**: Only an administrator or the role explicitly authorized to manage events/items may access and submit add_item.

**Unauthorized test case**: Log in as user1 or user2 obtain a fresh CSRF token and submit the add-item form.

**Authorization analysis (source code)**: post_add (add_item/) carries only @login_required and applies no role check: an ordinary authenticated user (user1) can open the add-item form and submit it, and the submitted NewsAndEvents item is saved directly. The neighboring management view edit_post additionally requires @lecturer_required, which the auditors took as the application's intended authorization policy for item/event management.

**Validation result**: user1 GET add_item/ returned 200 with the add-item form (CSRF token obtained); the POST returned 302 and created the item row with the token title in app_newsandevents (created=True); the form is likewise served to a visitor because the view has no authorization decorator.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-047.json](evidence/GT-047.json); [GT-047_gt047_user1_add_item_form.html](evidence/GT-047_gt047_user1_add_item_form.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| accounts/*, dashboard/, programs/*, quiz/*, result/*, semester/*, session/*, item/<pk>/delete/ (member and staff areas) | Protected member/staff areas | Request as visitor without a session | The requests are redirected to /accounts/login/; no content is exposed. |
| admin/* (Django admin site) | Protected Django administration | Request as visitor without a session | The requests are redirected to the admin login page; no admin content is exposed. |
| home, search/ (public pages) | Public pages | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for django_lms matched. The discussion item was the decorator policy: the neighboring edit_post view requires @login_required and @lecturer_required, establishing that item/event management is restricted to the lecturer/admin role, while post_add enforces neither role restriction. Both auditors agreed the user1-created item row is the unauthorized state change. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for django_lms

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-047 | `add_item/` | VPE | Confirmed |
