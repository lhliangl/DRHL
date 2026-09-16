# orangeforum Ground-Truth Audit Log

This log documents the complete independent manual audit of orangeforum that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Go server (the validation used a fresh build from the original source on http://localhost:9125/forums/localhost/), PostgreSQL 14.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: orangeforum is a Go forum application. The audit enumerated the comment and topic management endpoints and checked whether the edit/delete operations enforce resource ownership.

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

#### GT-049 - `categories/1/topics/9/comments/34/edit (Update)` (HPE)

**Expected authorization requirement**: Only the comment owner or an authorized moderator/administrator may update comment 34.

**Unauthorized test case**: Log in as user1 and submit an Update action for comment 34 owned by another ordinary user.

**Authorization analysis (source code)**: editComment processes the Update action via UpdateCommentByID(commentID, content, isSticky), which updates the comment row by id alone - no ownership check is applied. user1 (not the owner) can therefore update comment 34 owned by user2.

**Audit note**: Audit note: the validation was performed against a fresh build compiled from the original source, served on a separate port. Both auditors agreed the ground-truth records correspond to the original handlers.

**Validation result**: user1 GET categories/1/topics/9/comments/34/edit returned 200 with the edit form of user2's comment (content token exposed=True); the Update POST returned 303 and changed the comment content DRHLGT_c34_before_8703903437 -> DRHLGT_c34_after_8703903437 (updated=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-049.json](evidence/GT-049.json); [GT-049_gt049_user1_edit_form.html](evidence/GT-049_gt049_user1_edit_form.html)

#### GT-050 - `categories/1/topics/9/comments/34/edit (Delete)` (HPE)

**Expected authorization requirement**: Only the comment owner or an authorized moderator/administrator may delete comment 34.

**Unauthorized test case**: Log in as user1 and submit a Delete action for comment 34 owned by another ordinary user.

**Authorization analysis (source code)**: The Delete action calls DeleteCommentByID(commentID, userID, topicID), which deletes the row by id alone - the userID argument is only used to decrement the author's comment counter. user1 can delete comment 34 owned by user2.

**Validation result**: user1 GET categories/1/topics/9/comments/34/edit returned 200 with the edit form of user2's comment (token exposed=True); the Delete POST returned 303 and removed comment 34 (exists_after=0), with the topic comment counter decremented 5 -> 4.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-050.json](evidence/GT-050.json); [GT-050_gt050_user1_edit_form.html](evidence/GT-050_gt050_user1_edit_form.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| admin routes (/admin/*) | Protected administration | Request as a non-super-admin user | The handlers reject the request with HTTP 403 after checking user.IsSuperAdmin. |
| auth/signin (POST) | Authentication entry | Submit wrong credentials | The signin fails with the invalid-credentials message and no session token is issued. |
| index and topic/category browsing (GET) | Public forum content | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for orangeforum matched; both auditors agreed that the original handlers apply no ownership check to comment updates and deletes and that the confirmed cross-owner update and delete are the violations. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for orangeforum

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-049 | `categories/1/topics/9/comments/34/edit (Update)` | HPE | Confirmed |
| GT-050 | `categories/1/topics/9/comments/34/edit (Delete)` | HPE | Confirmed |
