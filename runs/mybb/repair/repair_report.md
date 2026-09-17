# DRHL Repair Report

- Repair Items: 1
- Total Repair Attempts: 3
- Patch Generation Attempts: 3
- Patches Generated: 3
- Failed Patches: 2
- Syntax / Compile OK: 3
- Exploit Blocked: 3
- Regression Passed: 1
- Database Validation Applied: 3
- Database Validation Passed: 1
- Successful Repairs: 1
- Failed Repairs: 0
- Successful on Attempt 1: 0
- Successful on Attempt 2: 0
- Successful on Attempt 3: 1

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `usercp2.php?action=addsubscription&fid=p1&type=forum`

- Category: admin_only
- Status: successful_repair
- Attempts: 3
- Patches Generated: 3
- Failed Patches: 2
- Syntax / Compile OK: 3
- Exploit Blocked: 3
- Regression Passed: 1
- Database Validation Applied: 3
- Database Validation Passed: 1
- Successful: true
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=False, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\mybb\repair\files\attempt-1\usercp2.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable; user1:not_vulnerable; user2:not_vulnerable); regression=(response=False; database=failed; evidence=authorized status=200; denial=['denial marker: password required'])
  - Attempt 2: syntax=True, exploit_blocked=True, regression=False, database_validation=False, successful=False
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\mybb\repair\files\attempt-2\usercp2.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable; user1:not_vulnerable; user2:not_vulnerable); regression=(response=False; database=failed; evidence=authorized status=200; denial=['denial marker: password required'])
  - Attempt 3: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(No syntax errors detected in D:\project\python\DRHL\runs\mybb\repair\files\attempt-3\usercp2.php); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable; user1:not_vulnerable; user2:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])
