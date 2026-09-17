# DRHL Repair Report

- Repair Items: 5
- Total Repair Attempts: 7
- Patch Generation Attempts: 7
- Patches Generated: 7
- Failed Patches: 2
- Syntax / Compile OK: 7
- Exploit Blocked: 5
- Regression Passed: 7
- Database Validation Applied: 3
- Database Validation Passed: 3
- Successful Repairs: 5
- Failed Repairs: 0
- Successful on Attempt 1: 4
- Successful on Attempt 2: 0
- Successful on Attempt 3: 1

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `control/db_backup.php`

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
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-1\control\db_backup.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=not_applicable; evidence=visitor:not_vulnerable); regression=(response=True; database=not_applicable; evidence=regression is not applicable because the vector has no authorized role)

### `install/index.php`

- Category: static_only
- Status: successful_repair
- Attempts: 3
- Patches Generated: 3
- Failed Patches: 2
- Syntax / Compile OK: 3
- Exploit Blocked: 1
- Regression Passed: 3
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful: true
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=False, regression=True, database_validation=True, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-1\install\index.php); deployment=(source patch applied); vulnerability_blocking=(response=False; database=not_applicable; evidence=visitor:vulnerable); regression=(response=True; database=not_applicable; evidence=regression is not applicable because the vector has no authorized role)
  - Attempt 2: syntax=True, exploit_blocked=False, regression=True, database_validation=True, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-2\install\index.php); deployment=(source patch applied); vulnerability_blocking=(response=False; database=not_applicable; evidence=visitor:vulnerable); regression=(response=True; database=not_applicable; evidence=regression is not applicable because the vector has no authorized role)
  - Attempt 3: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-3\install\index.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=not_applicable; evidence=visitor:not_vulnerable); regression=(response=True; database=not_applicable; evidence=regression is not applicable because the vector has no authorized role)

### `m_cp_avatar.php?KeepThis=true&TB_iframe=true&height=p1&width=p1`

- Category: authenticated_only
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
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-1\m_cp_avatar.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `member.php?id=1`

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
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-1\member.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=user1:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `member.php?id=p1`

- Category: horizontal
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
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\awcm\repair\files\attempt-1\member.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=user1:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])
