# DRHL Repair Report

- Repair Items: 3
- Total Repair Attempts: 3
- Patch Generation Attempts: 3
- Patches Generated: 3
- Failed Patches: 0
- Syntax / Compile OK: 3
- Exploit Blocked: 3
- Regression Passed: 3
- Database Validation Applied: 2
- Database Validation Passed: 2
- Successful Repairs: 3
- Failed Repairs: 0
- Successful on Attempt 1: 3
- Successful on Attempt 2: 0
- Successful on Attempt 3: 0

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `install.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\scarf\repair\files\attempt-1\install.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=not_applicable; evidence=visitor:not_vulnerable); regression=(response=True; database=not_applicable; evidence=regression is not applicable because the vector has no authorized role)

### `comments.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\scarf\repair\files\attempt-1\comments.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable; user1:not_vulnerable; user2:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `generaloptions.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\scarf\repair\files\attempt-1\generaloptions.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable; user1:not_vulnerable; user2:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])
