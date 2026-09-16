# Phpoll Ground-Truth Audit Log

This log documents the complete independent manual audit of Phpoll that produced its ground-truth vulnerability set, following the three-step procedure described in Section 5.1 (Ground-Truth Construction) of the paper: (1) independent auditing and authorization analysis, (2) uniform vulnerability validation, and (3) cross-checking and disagreement resolution. The audit was performed **without consulting DRHL's detection outputs**, and the ground-truth set was finalized **before any comparison with DRHL's detection reports**; the comparison (true positives, false positives, false negatives) is reported separately in the paper.

## Environment

- Date: 2026-09-14
- Deployment: local phpStudy installation (http://localhost/<app>/), MySQL 5.5.53, PHP 5.2.17.
- Auditors: two authors auditing independently; a third author reviews disagreements.

## Step 1 - Independent Auditing and Authorization Analysis

Two authors independently audited the application's source code and executable workflows, without consulting DRHL's detection outputs. They enumerated requestable endpoints and security-sensitive operations - protected-resource access as well as state-changing operations such as creation, modification, deletion, and administrative actions - and, for each operation, determined the expected authorization requirement from the application's role checks, identity and resource-ownership constraints, surrounding access-control logic, and normal application behavior.

**Application summary**: Phpoll's administrator area uses cookie-based login (phpoll_test_login / phpoll_test_password cookies set by admin/elabora_cookie.php) and the editor pages validate them. The audit checked every admin modification endpoint for the same validation.

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

#### GT-006 - `admin/modifica_band.php` (VPE)

**Expected authorization requirement**: Only an authenticated poll administrator may modify candidate or band data.

**Unauthorized test case**: Submit the modifica_band form as visitor without an administrator session.

**Authorization analysis (source code)**: admin/modifica_band.php processes the band-editor submission with no administrator-session check: it iterates the POST fields nome_band_i / voti_i / id_i and executes UPDATE phpoll_test_band ... WHERE id=... (or DELETE when the row is checked). A visitor POST rewrites band data directly.

**Validation result**: visitor POST to admin/modifica_band.php returned 200; band row id=69 nome_band changed DRHLGT_band_before_8670657866 -> DRHLGT_band_after_8670657866 (updated=True).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-006.json](evidence/GT-006.json)

#### GT-007 - `admin/modifica_configurazione.php` (VPE)

**Expected authorization requirement**: Only an authenticated poll administrator may change poll configuration.

**Unauthorized test case**: Submit configuration changes as visitor without an administrator session.

**Authorization analysis (source code)**: admin/modifica_configurazione.php TRUNCATEs phpoll_test_configurazione and re-inserts one row from the POST values (including the admin login/password fields and the bar color values) with no administrator-session check. A visitor POST rewrites the entire poll configuration.

**Validation result**: visitor POST to admin/modifica_configurazione.php returned 200; configuration was truncated and rewritten: oggetto_email DRHLGT_cfg_before_8670658713 -> DRHLGT_cfg_after_8670658713 (updated=True); barra*.gif image files were restored afterwards.

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-007.json](evidence/GT-007.json)

#### GT-008 - `admin/modifica_votanti.php` (VPE)

**Expected authorization requirement**: Only an authenticated poll administrator may modify voter or voting data.

**Unauthorized test case**: Submit the voter-management form as visitor without an administrator session.

**Authorization analysis (source code)**: admin/modifica_votanti.php deletes voter rows (and decrements band vote counters for the bands named in the deleted row) from the POST keys with no administrator-session check. A visitor POST deletes voter data directly.

**Validation result**: visitor POST to admin/modifica_votanti.php returned 200; instrumented voter row id=9 (ip=DRHLGT_voter_8670659608) was deleted (exists_after=0).

**Ground-truth entry**: Confirmed (the unauthorized operation succeeded).

**Experiment record**: [GT-008.json](evidence/GT-008.json)

### Negative testing of properly protected operations

The auditors also executed unauthorized test cases for the remaining security-sensitive operations of the application - the ones whose authorization checks the Step-1 audit found present in the code. Every one of these test cases was properly denied, so these operations were **not** entered into the ground truth:

| Operation | Expected authorization | Unauthorized test case | Observed denial |
|---|---|---|---|
| admin/band_editor.php, admin/config_editor.php, admin/votanti.php (GET, POST) | Protected administrator editor access | Request as visitor without the administrator login cookies | The response renders the login form with a login denial message; the editors are not exposed. |
| cookies/conta.php, cookies/contatutto.php (GET) | Protected cookie administration | Request as visitor | The response carries the password denial message; the administration function is not exposed. |
| cookies/resetta_cookie.php (GET) | Protected cookie reset | Request as visitor | The unauthorized response body is empty; no reset is performed. |
| admin/index.php, admin/risultati_config.php, cookies/risultati_perc.php, cookies/setta_cookie.php (GET) | Public poll/config display pages | Request as visitor | These pages are public by design (no authorization requirement), so successful access is not a vulnerability. |

## Step 3 - Cross-Checking and Disagreement Resolution

The two auditors' candidate sets for Phpoll matched; the only discussion item was the file-system side effect of GT-007 (the bar color GIFs are regenerated), which was handled by backing up and restoring the files during validation. The set was finalized before any comparison with DRHL's detection outputs.

## Finalized Ground-Truth Set for Phpoll

| ID | Endpoint / Operation | BAC Type | Verdict |
|---|---|---|---|
| GT-006 | `admin/modifica_band.php` | VPE | Confirmed |
| GT-007 | `admin/modifica_configurazione.php` | VPE | Confirmed |
| GT-008 | `admin/modifica_votanti.php` | VPE | Confirmed |
