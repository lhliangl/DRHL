# DRHL Repair Report

- Repair Items: 7
- Total Repair Attempts: 10
- Patch Generation Attempts: 10
- Patches Generated: 10
- Failed Patches: 3
- Syntax / Compile OK: 10
- Exploit Blocked: 10
- Regression Passed: 7
- Database Validation Applied: 5
- Database Validation Passed: 3
- Successful Repairs: 7
- Failed Repairs: 0
- Successful on Attempt 1: 5
- Successful on Attempt 2: 1
- Successful on Attempt 3: 1

> Patches Generated counts every generated patch file, including patches that later failed syntax, exploit-blocking, or regression validation.
> Total Repair Attempts counts how many LLM repair attempts were consumed across all repair items, including failed attempts and items that exhausted the retry budget.
> Validation has three dimensions: syntax/compile, vulnerability blocking, and authorized regression. For the latter two, both the response oracle and each matching database oracle phase must pass.
> Runtime validation may temporarily apply a patch to the source tree, but the original web application files are restored before this report is written.

## Details

### `admin/addnews.jsp`

- Category: admin_only
- Status: successful_repair
- Attempts: 2
- Patches Generated: 2
- Failed Patches: 1
- Syntax / Compile OK: 2
- Exploit Blocked: 2
- Regression Passed: 1
- Database Validation Applied: 0
- Database Validation Passed: 0
- Successful: true
- Message: syntax/compile, vulnerability blocking, and regression validation all passed

  - Attempt 1: syntax=True, exploit_blocked=True, regression=False, database_validation=True, successful=False
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=False; database=passed; evidence=authorized status=302; denial=['denial redirect: http://localhost:8080/blog/admin/index.jsp'])
  - Attempt 2: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/addnews2.jsp`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=failed; evidence=authorized status=302; denial=['denial redirect: http://localhost:8080/blog/admin/index.jsp']; authorized success redirect accepted)
  - Attempt 2: syntax=True, exploit_blocked=True, regression=False, database_validation=False, successful=False
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=failed; evidence=authorized status=302; denial=['denial redirect: http://localhost:8080/blog/admin/index.jsp']; authorized success redirect accepted)
  - Attempt 3: syntax=True, exploit_blocked=True, regression=True, database_validation=True, successful=True
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/adduser.jsp`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/adduser2.jsp`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/admin.jsp`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/editnews.jsp`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])

### `admin/editnews2.jsp?body=p1&headline=AokwZT`

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
    - Message: syntax=(syntax check disabled by configuration); deployment=(source patch applied); vulnerability_blocking=(response=True; database=passed; evidence=visitor:not_vulnerable); regression=(response=True; database=passed; evidence=authorized status=200; denial=[])
