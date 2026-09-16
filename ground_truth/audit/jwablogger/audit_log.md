# jwablogger Ground-Truth Audit Log

This log documents the complete independent manual audit of jwablogger that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Tomcat 9 deployment (http://localhost:8080/jwablogger/), MySQL 5.5.53.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: jwablogger exposes blog content through the /blogger/viewEntry/{id}/{internalName}.html handler. The audit checked whether non-visible entries (is_visible='false') are filtered in the viewEntry handler. The visibility flag is applied only in the listing queries; the viewEntry handler serves the entry content without consulting it, and responses are cached (ehcache).

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

#### GT-045 - `blogger/viewEntry/5444/drhl_test_entry.html` (VPE)

**Expected authorization requirement**: An entry with isVisible=false must be available only to an authorized administrator or owner according to the application policy.

**Unauthorized test case**: Request the non-visible entry as visitor.

**Authorization analysis (source code)**: The viewEntry handler serves the full entry content (title, description, and body text) without checking is_visible: a visitor request for an entry whose is_visible='false' returns the complete entry page.

**Audit note**: Audit note: the released endpoint text names entry 5444/drhl_test_entry from the original deployment; in the current deployment that id is a cached seeded row, so the validation inserted a fresh entry with is_visible='false' (documented precondition; the first fetch is uncached) and additionally requested a naturally non-visible entry as supporting evidence. The database baseline was restored after the record.

**Validation result**: visitor GET blogger/viewEntry/5445 returned 200 and served the full content of the fresh entry with is_visible='false' (token exposed=True); a naturally non-visible entry (1927) is likewise served (exposed=True), while entry creation requires login (denied=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-045.json](evidence/GT-045.json); [GT-045_gt045_visitor_new_entry.html](evidence/GT-045_gt045_visitor_new_entry.html); [GT-045_gt045_visitor_1927.html](evidence/GT-045_gt045_visitor_1927.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| blogger/saveEntry (POST, entry creation) | Protected entry creation (requires login) | Submit as visitor without a session | The response carries the 'Must be logged in' denial; no entry is created. |
| blogger (index), blogger/search, blogger/saveComment | Public blog browsing / comment submission | Request as visitor | Public by design; not vulnerabilities. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for jwablogger matched. The discussion item was the response cache: the seeded entry named in the released table is served from cache, so the validation used a fresh non-visible entry (documented precondition) plus a naturally non-visible entry without any precondition; both confirmed that is_visible is not consulted by the viewEntry handler. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for jwablogger

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-045 | `blogger/viewEntry/5444/drhl_test_entry.html` | VPE | Confirmed |
