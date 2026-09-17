# DRHL Repair Report

- Repair Items: 5
- Total Repair Attempts: 5
- Patch Generation Attempts: 5
- Patches Generated: 5
- Failed Patches: 0
- Syntax / Compile OK: 5
- Exploit Blocked: 5
- Regression Passed: 5
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful Repairs: 5
- Failed Repairs: 0
- Successful on Attempt 1: 5
- Successful on Attempt 2: 0
- Successful on Attempt 3: 0

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `backdoor.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\bwapp\repair\files\attempt-1\backdoor.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=regression is not applicable because the vector has no authorized role)

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\bwapp\repair\files\attempt-1\install.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=regression is not applicable because the vector has no authorized role)

### `secret-cors-1.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\bwapp\repair\files\attempt-1\secret-cors-1.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=regression is not applicable because the vector has no authorized role)

### `secret-cors-2.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\bwapp\repair\files\attempt-1\secret-cors-2.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=regression is not applicable because the vector has no authorized role)

### `secret-cors-3.php`

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
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\bwapp\repair\files\attempt-1\secret-cors-3.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=regression is not applicable because the vector has no authorized role)
