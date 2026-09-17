# DRHL Repair Report

- Repair Items: 1
- Total Repair Attempts: 3
- Patch Generation Attempts: 3
- Patches Generated: 3
- Failed Patches: 2
- Syntax / Compile OK: 3
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 0
- Database Validation Passed: 0
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

### `eee/`

- Category: authenticated_only
- Status: successful_repair
- Attempts: 3
- Patches Generated: 3
- Failed Patches: 2
- Syntax / Compile OK: 3
- Exploit Blocked: 1
- Regression Passed: 1
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful: true
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=False, regression=False, database_validation=False, successful=False
    - Message: syntax=(py_compile exited with 0); runtime deployment hook failed: repair.validation.reload_command exited with 1: [djangoblog_server] stopped PID 13792
[djangoblog_server] started PID 33140: http://localhost:8000/

[djangoblog_server] timed out waiting for http://localhost:8000/; see D:\project\python\DRHL\database_recovery\djangoblog\runserver.stderr.log
  - Attempt 2: syntax=True, exploit_blocked=False, regression=False, database_validation=False, successful=False
    - Message: syntax=(py_compile exited with 0); runtime deployment hook failed: repair.validation.reload_command exited with 1: [djangoblog_server] stopped PID 19040
[djangoblog_server] started PID 12664: http://localhost:8000/

[djangoblog_server] timed out waiting for http://localhost:8000/; see D:\project\python\DRHL\database_recovery\djangoblog\runserver.stderr.log
  - Attempt 3: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(py_compile exited with 0); deployment=(source patch applied; reload=([djangoblog_server] stopped PID 8128
[djangoblog_server] started PID 35332: http://localhost:8000/
[djangoblog_server] ready: http://localhost:8000/)); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])
