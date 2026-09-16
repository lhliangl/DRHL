# DjangoBlog Ground-Truth Audit Log

This log documents the complete independent manual audit of DjangoBlog that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Django 2.1.7 development server (http://localhost:8000/), SQLite database.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: DjangoBlog renders blog posts through the PostList and PostDetail class-based views. The Post model carries a status field (1 = published, 0 = unpublished). The audit checked whether the post-detail route applies the same status filter as the list view.

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

#### GT-046 - `eee/ (unpublished PostDetail)` (VPE)

**Expected authorization requirement**: A post with status=0 must be visible only to a staff user; visitors must receive a not-found or denial response.

**Unauthorized test case**: Request an unpublished post (status=0) as visitor (the validation used a freshly inserted unpublished post with marker tokens in its title and content).

**Authorization analysis (source code)**: PostList filters the queryset by status=1, but PostDetail is a plain DetailView over the whole Post model: it renders any post selected by slug regardless of its status. A visitor requesting an unpublished post slug receives the complete post page instead of a not-found response.

**Audit note**: The validation inserted a fresh unpublished post (status=0) with marker tokens in its title and content, requested it as a visitor, and deleted the inserted post afterwards. Both auditors agreed that the status filter of the list view is not applied to the detail view.

**Validation result**: a fresh unpublished post (status=0) with marker tokens was inserted; visitor GET /drhlgt_unpublished_8707965774/ returned 200 and served the unpublished post content (token exposed=True); the inserted post was deleted afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-046.json](evidence/GT-046.json); [GT-046_gt046_visitor_unpublished.html](evidence/GT-046_gt046_visitor_unpublished.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| PostList (home page, GET) | Public post listing | Request as visitor | Only published posts (status=1) are listed, as intended; public by design. |
| Unknown slug (PostDetail, GET) | Post detail for a nonexistent slug | Request as visitor | Django returns the standard 404 page; no content is exposed. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for DjangoBlog matched. The discussion item was the deployment state of views.py (recorded in GT-046); both auditors agreed that the list view applies the status filter while the detail view does not, and that the visitor-rendered unpublished post page is the violation. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for DjangoBlog

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-046 | `eee/ (unpublished PostDetail)` | VPE | Confirmed |
