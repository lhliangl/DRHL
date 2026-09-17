# DRHL Repair Report

- Repair Items: 1
- Total Repair Attempts: 1
- Patch Generation Attempts: 1
- Patches Generated: 1
- Failed Patches: 0
- Syntax / Compile OK: 1
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful Repairs: 1
- Failed Repairs: 0
- Successful on Attempt 1: 1
- Successful on Attempt 2: 0
- Successful on Attempt 3: 0

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `bbs_pub/`

- Category: admin_only
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
    - Message: syntax=(py_compile exited with 0); deployment=(source patch applied; reload=([djangoblog_server] stopped PID 27580
[djangoblog_server] started PID 30664: http://127.0.0.1:8000/
[djangoblog_server] ready: http://127.0.0.1:8000/)); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=302; denial=[])
