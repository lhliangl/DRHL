# DRHL Repair Report

- Repair Items: 2
- Total Repair Attempts: 2
- Patch Generation Attempts: 2
- Patches Generated: 2
- Failed Patches: 0
- Syntax / Compile OK: 2
- Exploit Blocked: 2
- Regression Passed: 2
- Database Validation Applied: 1
- Database Validation Passed: 1
- Successful Repairs: 2
- Failed Repairs: 0
- Successful on Attempt 1: 2
- Successful on Attempt 2: 0
- Successful on Attempt 3: 0

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `admin/setup.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\events_lister\repair\files\attempt-1\admin\setup.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=not_applicable; evidence=GET: visitor:not_vulnerable); regression=(response=True; database=not_applicable; evidence=GET: regression is not applicable because the vector has no authorized role)

### `admin/user_add.php`

- Category: admin_only
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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\events_lister\repair\files\attempt-1\admin\user_add.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=POST: visitor:not_vulnerable); regression=(response=True; database=passed; evidence=POST: authorized status=200; denial=[])
