# Jspblog Ground-Truth Audit Log

This log documents the complete independent manual audit of Jspblog that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Tomcat 9 deployment (http://localhost:8080/blog/), MySQL 5.5.53.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: Jspblog's administration area consists of JSP pages under /admin/. The login page (admin/index.jsp submitted to admin/index2.jsp) sets the session attribute isLoggedIn after checking the hard-coded admin credentials, but none of the administrative pages ever consult the session: every admin page executes its operation unconditionally. The audit enumerated all functional admin pages.

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

#### GT-032 - `admin/addnews.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may open the add-news form.

**Unauthorized test case**: Request admin/addnews.jsp as visitor.

**Authorization analysis (source code)**: addnews.jsp renders the add-news form (author select plus headline/body fields) with no session check; the form is served to any visitor.

**Validation result**: visitor GET admin/addnews.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-032.json](evidence/GT-032.json); [GT-032_GT-032_visitor.html](evidence/GT-032_GT-032_visitor.html)

#### GT-033 - `admin/addnews2.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may create a news item.

**Unauthorized test case**: Submit headline and body parameters to admin/addnews2.jsp as visitor.

**Authorization analysis (source code)**: addnews2.jsp executes INSERT INTO news (headline, body, date, author) from request parameters with no session check; a visitor POST creates a news row.

**Validation result**: visitor POST admin/addnews2.jsp returned 200; a news row with the token headline was created in the portal database (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-033.json](evidence/GT-033.json); [GT-033_gt033_visitor.html](evidence/GT-033_gt033_visitor.html)

#### GT-034 - `admin/adduser.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may open the user-creation form.

**Unauthorized test case**: Request admin/adduser.jsp as visitor.

**Authorization analysis (source code)**: adduser.jsp renders the user-creation form (author/name fields) with no session check; the form is served to any visitor.

**Validation result**: visitor GET admin/adduser.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-034.json](evidence/GT-034.json); [GT-034_GT-034_visitor.html](evidence/GT-034_GT-034_visitor.html)

#### GT-035 - `admin/adduser2.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may create an application user.

**Unauthorized test case**: Submit a new user payload to admin/adduser2.jsp as visitor.

**Authorization analysis (source code)**: adduser2.jsp executes INSERT INTO user (name, author) with no session check; a visitor POST creates an application user.

**Validation result**: visitor POST admin/adduser2.jsp returned 200; a user row with the token name was created in the portal database (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-035.json](evidence/GT-035.json); [GT-035_gt035_visitor.html](evidence/GT-035_gt035_visitor.html)

#### GT-036 - `admin/admin.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may access the administration dashboard.

**Unauthorized test case**: Request admin/admin.jsp as visitor.

**Authorization analysis (source code)**: admin.jsp renders the administration control-panel menu (links to every admin operation) with no session check; the dashboard is served to any visitor.

**Validation result**: visitor GET admin/admin.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-036.json](evidence/GT-036.json); [GT-036_GT-036_visitor.html](evidence/GT-036_GT-036_visitor.html)

#### GT-037 - `admin/editnews.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may access the news-management and edit-selection page.

**Unauthorized test case**: Request admin/editnews.jsp as visitor.

**Authorization analysis (source code)**: editnews.jsp lists every news row together with an edit form (headline/body) with no session check; the news-management page is served to any visitor.

**Validation result**: visitor GET admin/editnews.jsp returned 200; the news-management page lists the news rows and exposed the token injected into a news body (exposed=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-037.json](evidence/GT-037.json); [GT-037_gt037_visitor.html](evidence/GT-037_gt037_visitor.html)

#### GT-038 - `admin/editnews2.jsp` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may open or submit the news-edit operation.

**Unauthorized test case**: Request or submit admin/editnews2.jsp with headline and body parameters as visitor.

**Authorization analysis (source code)**: editnews2.jsp executes UPDATE news SET body=... with no session check; the query carries no WHERE clause, so one visitor POST rewrites the body of every news row.

**Validation result**: visitor POST admin/editnews2.jsp returned 200; the news body changed DRHLGT_news_before_8684168024 -> DRHLGT_news_after_8684168024 in the portal database (updated=True; the query carries no WHERE clause, so it applies to every row).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-038.json](evidence/GT-038.json); [GT-038_gt038_visitor.html](evidence/GT-038_gt038_visitor.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| admin/index.jsp + admin/index2.jsp (login flow) | Administrator authentication entry | Request as visitor | The login page renders only the login form; index2.jsp establishes the session only for the hard-coded admin credentials, and no admin function is exposed without it. |
| blog index.jsp and the public entry view | Public blog content | Request as visitor | Public by design; not vulnerabilities. |
| delnews.jsp / deluser.jsp / edituser.jsp (control-panel menu links) | Dead menu links | Request as visitor | The target files do not exist in this deployment; the linked operations are unavailable. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for Jspblog matched. The discussion items were the dead menu links (the files do not exist in this deployment) and the confirmation that the login session attribute is never consulted by any admin page (traced through all admin JSPs). The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for Jspblog

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-032 | `admin/addnews.jsp` | VPE | Confirmed |
| GT-033 | `admin/addnews2.jsp` | VPE | Confirmed |
| GT-034 | `admin/adduser.jsp` | VPE | Confirmed |
| GT-035 | `admin/adduser2.jsp` | VPE | Confirmed |
| GT-036 | `admin/admin.jsp` | VPE | Confirmed |
| GT-037 | `admin/editnews.jsp` | VPE | Confirmed |
| GT-038 | `admin/editnews2.jsp` | VPE | Confirmed |
