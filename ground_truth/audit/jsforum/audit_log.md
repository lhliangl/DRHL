# JsForum Ground-Truth Audit Log

This log documents the complete independent manual audit of JsForum that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, Tomcat 9 deployment (http://localhost:8080/JsForum/), MySQL 5.5.53.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: JsForum maps its actions to servlets under /servlet/forum.*. The servlets AddForum, AddReply, and AddThread contain no session check at all and take the message author from a request parameter; forum/editmessage.jsp renders the edit form of any message to any authenticated session without an ownership check. The audit enumerated the forum write actions and the message/edit pages.

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

#### GT-039 - `servlet/forum.AddForum` (VPE)

**Expected authorization requirement**: Only an authenticated administrator may create a forum.

**Unauthorized test case**: Submit AddForum as visitor or an ordinary user.

**Authorization analysis (source code)**: AddForum inserts the new forum (forum_id = lastforum_id + 1, title, forum_info) with no session or role check; a visitor or any ordinary user creates a forum.

**Validation result**: visitor POST servlet/forum.AddForum returned 302; a forum row with the token title was created in the forum database (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-039.json](evidence/GT-039.json)

#### GT-040 - `servlet/forum.AddReply` (VPE)

**Expected authorization requirement**: Only an authenticated user may create a reply.

**Unauthorized test case**: Submit AddReply as visitor without a session.

**Authorization analysis (source code)**: AddReply inserts the reply (forum_id, thread_id, reply_id = lastReply_id + 1, message, user) with no session check; the author is taken from the user request parameter, so a visitor creates replies.

**Validation result**: visitor POST servlet/forum.AddReply returned 302; a reply row with the token message was created in forum_message (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-040.json](evidence/GT-040.json)

#### GT-041 - `servlet/forum.AddThread` (VPE)

**Expected authorization requirement**: Only an authenticated user may create a thread.

**Unauthorized test case**: Submit AddThread as visitor without a session.

**Authorization analysis (source code)**: AddThread inserts the thread (forum_id, thread_id = lastThread_id + 1, title, views=0) and its initial forum_message row with no session check; the author is taken from the user request parameter, so a visitor creates threads.

**Validation result**: visitor POST servlet/forum.AddThread returned 302; a thread row with the token title was created in forum_threads (created=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-041.json](evidence/GT-041.json)

#### GT-042 - `servlet/forum.AddReply with user=user2` (HPE)

**Expected authorization requirement**: The author of a new reply must be derived from the authenticated session and must not be selected by a request parameter.

**Unauthorized test case**: Log in as user1 and submit AddReply with the user parameter changed to user2.

**Authorization analysis (source code)**: Same defect as GT-040 exercised horizontally: logged in as user1, the user parameter is set to user2 and the created reply is recorded under user2, although the author must be derived from the authenticated session.

**Validation result**: user1 POST servlet/forum.AddReply with the user parameter set to user2 returned 302; the created content carries user2 as its author although the session belongs to user1 (author_forged=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-042.json](evidence/GT-042.json)

#### GT-043 - `servlet/forum.AddThread with user=user2` (HPE)

**Expected authorization requirement**: The author of a new thread and its initial message must be derived from the authenticated session.

**Unauthorized test case**: Log in as user1 and submit AddThread with the user parameter changed to user2.

**Authorization analysis (source code)**: Same defect as GT-041 exercised horizontally: logged in as user1, the user parameter is set to user2 and the initial message of the created thread is recorded under user2, although the author must be derived from the authenticated session.

**Validation result**: user1 POST servlet/forum.AddThread with the user parameter set to user2 returned 302; the created content carries user2 as its author although the session belongs to user1 (author_forged=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-043.json](evidence/GT-043.json)

#### GT-044 - `forum/editmessage.jsp (reply of another user)` (HPE)

**Expected authorization requirement**: The edit interface of a message must be available only to the message author or an administrator; a user must not open the edit form of another user's message.

**Unauthorized test case**: Log in as user1 and open forum/editmessage.jsp for a reply authored by user2.

**Authorization analysis (source code)**: forum/editmessage.jsp loads the message selected by forum_id/thread_id/reply_id and renders it in the edit form for any authenticated session without checking that the session user is the message author: user1 opens the edit interface of user2's reply and the form contains user2's message content. The ChangeMessage write, by contrast, is owner-gated for non-admin users (UPDATE ... AND user=sessionUsername), which bounds the impact of the defect.

**Validation result**: user1 GET forum/editmessage.jsp for user2's reply returned 200; the edit form rendered user2's message content (token exposed=True); the submitted ChangeMessage left the row unchanged (write owner-gated=True), bounding the impact to the unauthorized edit-interface access.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-044.json](evidence/GT-044.json); [GT-044_gt044_user1_editmessage.html](evidence/GT-044_gt044_user1_editmessage.html)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| forum/forum.jsp, forum/thread.jsp, forum/profile.jsp (member pages) | Protected member pages | Request as visitor without a session | The responses carry the 'you have to login first' denial and the login form; no member content is exposed. |
| forum/editmessage.jsp (visitor access) | Edit-interface access for unauthenticated visitors | Request as visitor without a session | The response terminates with an exception trace and no edit form is rendered; the form is only rendered for authenticated sessions (see GT-044 for the cross-user access among authenticated users). |
| servlet/forum.ChangeMessage, servlet/forum.ChangeProfile (state-changing servlets) | Protected message/profile changes | Request as visitor without a session | The responses are empty (silent termination); no state change is performed. |
| servlet/forum.DeleteForum, servlet/forum.DeleteReply, servlet/forum.DeleteThread (deletion servlets) | Protected deletion actions | Request as an ordinary user | The responses are empty (silent termination); no deletion is performed. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for JsForum matched. The discussion item was GT-044: the edit form of another user's reply is rendered to any authenticated user, while the submitted ChangeMessage left the target row unchanged (the write is owner-gated for non-admin users); both auditors agreed the unauthorized edit-interface access is the violation and recorded the owner-gated write as its boundary. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for JsForum

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-039 | `servlet/forum.AddForum` | VPE | Confirmed |
| GT-040 | `servlet/forum.AddReply` | VPE | Confirmed |
| GT-041 | `servlet/forum.AddThread` | VPE | Confirmed |
| GT-042 | `servlet/forum.AddReply with user=user2` | HPE | Confirmed |
| GT-043 | `servlet/forum.AddThread with user=user2` | HPE | Confirmed |
| GT-044 | `forum/editmessage.jsp (reply of another user)` | HPE | Confirmed |
