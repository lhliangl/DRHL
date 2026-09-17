# DRHL Repair Report

- Repair Items: 7
- Total Repair Attempts: 14
- Patch Generation Attempts: 14
- Patches Generated: 13
- Failed Patches: 8
- Syntax / Compile OK: 13
- Exploit Blocked: 7
- Regression Passed: 11
- Database Validation Applied: 12
- Database Validation Passed: 4
- Successful Repairs: 5
- Failed Repairs: 2
- Successful on Attempt 1: 2
- Successful on Attempt 2: 3
- Successful on Attempt 3: 0

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> A repair is counted as successful only when syntax/compile, exploit-blocking, regression validation, and every matching repair database oracle all pass for the same generated patch.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `install/index.php`

- Category: static_only
- Status: successful_repair
- Attempts: 1
- Patches Generated: 1
- Failed Patches: 0
- Syntax / Compile OK: 1
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful: true
- Message: syntax/compile, exploit blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\install\index.php); deployment=(source patch applied); exploit=(visitor:not_vulnerable); regression=(regression is not applicable because the vector has no authorized role); database_validation=(not_configured)

### `article.php?action=delete&do=comments&id=6`

- Category: vertical
- Status: successful_repair
- Attempts: 1
- Patches Generated: 1
- Failed Patches: 0
- Syntax / Compile OK: 1
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 1
- Database Validation Passed: 1
- Successful: true
- Message: syntax/compile, exploit blocking, regression, and database validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\article.php); deployment=(source patch applied); exploit=(register:not_vulnerable); regression=(authorized status=200; denial=[]); database_validation=(passed:GT-011-comment-delete:passed)

### `article.php?do=comments&id=6`

- Category: vertical
- Status: successful_repair
- Attempts: 2
- Patches Generated: 1
- Failed Patches: 0
- Syntax / Compile OK: 1
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 1
- Database Validation Passed: 1
- Successful: true
- Message: syntax/compile, exploit blocking, regression, and database validation all passed

  - Attempt 1: syntax=False, exploit_blocked=False, regression=False, database_validation=True, successful=False
    - Message: attempt error: JSONDecodeError: Expecting value: line 1 column 1 (char 0)
  - Attempt 2: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-2\article.php); deployment=(source patch applied); exploit=(register:not_vulnerable); regression=(authorized status=200; denial=[]); database_validation=(passed:GT-010-comment-management-read:passed)

### `article.php?do=edit&id=p1`

- Category: horizontal
- Status: repair_failed
- Attempts: 3
- Patches Generated: 3
- Failed Patches: 3
- Syntax / Compile OK: 3
- Exploit Blocked: 2
- Regression Passed: 1
- Database Validation Applied: 3
- Database Validation Passed: 0
- Successful: false
- Message: repair failed after maximum attempts

  - Attempt 1: syntax=True, exploit_blocked=True, regression=False, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\article.php); deployment=(source patch applied); exploit=(user1:not_vulnerable); regression=(authorized status=302; denial=['denial redirect: http://localhost/phpns/index.php?do=permissiondenied']); database_validation=(failed:GT-012-article-edit-read:failed[authorized:response_contains expected=DRHLR_5a74a7d9276e observed=<response>])
  - Attempt 2: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-2\article.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-012-article-edit-read:failed[attack:response_not_contains expected=DRHLR_3bed9339a270 observed=<response>])
  - Attempt 3: syntax=True, exploit_blocked=True, regression=False, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-3\article.php); deployment=(source patch applied); exploit=(user1:not_vulnerable); regression=(authorized status=302; denial=['denial redirect: http://localhost/phpns/index.php?do=permissiondenied']); database_validation=(failed:GT-012-article-edit-read:failed[authorized:response_contains expected=DRHLR_8f3b9b7d4bfc observed=<response>])

### `article.php?do=editp&id=p1`

- Category: horizontal
- Status: repair_failed
- Attempts: 3
- Patches Generated: 3
- Failed Patches: 3
- Syntax / Compile OK: 3
- Exploit Blocked: 0
- Regression Passed: 3
- Database Validation Applied: 3
- Database Validation Passed: 0
- Successful: false
- Message: repair failed after maximum attempts

  - Attempt 1: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\article.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-013-article-edit-update:failed[authorized:scalar_equals expected=DRHLR_9e78eea44eb6_AFTER observed=DRHLR_9e78eea44eb6_BEFORE])
  - Attempt 2: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-2\article.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-013-article-edit-update:failed[authorized:scalar_equals expected=DRHLR_06299e8a6c1b_AFTER observed=DRHLR_06299e8a6c1b_BEFORE])
  - Attempt 3: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-3\article.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-013-article-edit-update:failed[authorized:scalar_equals expected=DRHLR_306f2447774f_AFTER observed=DRHLR_306f2447774f_BEFORE])

### `user.php?do=edit&id=p1`

- Category: horizontal
- Status: successful_repair
- Attempts: 2
- Patches Generated: 2
- Failed Patches: 1
- Syntax / Compile OK: 2
- Exploit Blocked: 1
- Regression Passed: 2
- Database Validation Applied: 2
- Database Validation Passed: 1
- Successful: true
- Message: syntax/compile, exploit blocking, regression, and database validation all passed

  - Attempt 1: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\user.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-014-user-edit-read:failed[attack:response_not_contains expected=DRHLR_9b857621c49d observed=<response>])
  - Attempt 2: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-2\user.php); deployment=(source patch applied); exploit=(user1:not_vulnerable); regression=(authorized status=200; denial=[]); database_validation=(passed:GT-014-user-edit-read:passed)

### `user.php?do=editp`

- Category: horizontal
- Status: successful_repair
- Attempts: 2
- Patches Generated: 2
- Failed Patches: 1
- Syntax / Compile OK: 2
- Exploit Blocked: 1
- Regression Passed: 2
- Database Validation Applied: 2
- Database Validation Passed: 1
- Successful: true
- Message: syntax/compile, exploit blocking, regression, and database validation all passed

  - Attempt 1: syntax=True, exploit_blocked=False, regression=True, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-1\user.php); deployment=(source patch applied); exploit=(user1:vulnerable); regression=(authorized status=200; denial=[]); database_validation=(failed:GT-015-user-edit-update:failed[attack:scalar_equals expected=DRHLR_d3e510fce7b1_BEFORE observed=DRHLR_d3e510fce7b1_AFTER])
  - Attempt 2: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\phpns\repair\files\attempt-2\user.php); deployment=(source patch applied); exploit=(user1:not_vulnerable); regression=(authorized status=200; denial=[]); database_validation=(passed:GT-015-user-edit-update:passed)
