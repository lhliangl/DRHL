# Repair-only database validation

Repair validation is organized around three dimensions:

1. syntax/compile validity;
2. vulnerability blocking;
3. authorized regression behavior.

The latter two dimensions combine two signals. The response oracle checks the
HTTP behavior, while a configuration-driven database/content oracle checks the
application effect. Database/content rules are configured through
`repair.validation.database_oracles` and are evaluated only by the repair
stage; active vulnerability detection does not read or execute them.

Each matching rule runs twice from the database baseline and contributes one
phase to each behavioral dimension:

1. `attack` joins the response exploit check in the vulnerability-blocking
   dimension. It replays the unauthorized request and checks that protected
   content or a database mutation is absent.
2. `authorized` joins the authorized response check in the regression
   dimension. It rebuilds the same precondition, replays the legitimate
   request, and checks that the intended read or mutation still succeeds.

Set `session_before_setup` to `true` on a phase when its setup SQL changes a
field needed to authenticate that phase. DRHL will establish the role session
from the clean baseline first, execute the setup SQL, and then replay the
request. The default remains `false`.

The baseline is restored before each phase and again after each scenario. A
patch succeeds only when syntax/compile passes, both vulnerability-blocking
oracles pass, and both regression oracles pass. If no database rule matches,
that second signal is not applicable and the response oracle remains decisive.

The LLM receives only dimension-level retry reasons such as "the vulnerability
was not blocked" or "the regression test did not pass." SQL, table/column
names, query results, marker values, response evidence, and oracle identifiers
remain in the local validation artifact and are never included in LLM feedback.

## Skipping a repair finding

`repair.skip_findings` can exclude a detected finding from repair generation
without removing it from detection results. Each entry must select a `page` or
`page_pattern` and may also select a `category`. An optional `reason` is emitted
in repair progress output. This is useful when one shared implementation patch
covers another reported route; attach the covered route's oracle to the repair
that is still generated so the shared fix remains explicitly validated.

## Configuration shape

```json
{
  "repair": {
    "validation": {
      "database_oracles": [
        {
          "name": "edit-other-user",
          "page_pattern": "^user\\.php\\?do=edit",
          "category": "horizontal",
          "operation": "update",
          "variables": {
            "target_id": {"query": "SELECT id FROM users WHERE username='user2' LIMIT 1"}
          },
          "setup_sql": [
            "UPDATE users SET display_name='{token1}' WHERE id={target_id}"
          ],
          "attack": {
            "role": "user1",
            "request": {
              "page": "user.php?do=save",
              "method": "POST",
              "replace_params": true,
              "params": {"id": "{target_id}", "display_name": "{token2}"}
            },
            "assert": {
              "query": "SELECT display_name FROM users WHERE id={target_id}",
              "scalar_equals": "{token1}"
            }
          },
          "authorized": {
            "role": "user2",
            "request": {
              "page": "user.php?do=save",
              "method": "POST",
              "replace_params": true,
              "params": {"id": "{target_id}", "display_name": "{token2}"}
            },
            "assert": {
              "query": "SELECT display_name FROM users WHERE id={target_id}",
              "scalar_equals": "{token2}"
            }
          }
        }
      ]
    }
  }
}
```

Rules match the repair attack vector through `page` or `page_pattern`; an
optional `category` further restricts the match. Multiple rules may match one
repair, which allows one patch to be checked against both a read form and its
state-changing submit action.

Available unique placeholders are `{token}`, `{token1}`, and `{token2}`.
Additional placeholders can be declared under `variables`; a value can be a
literal or an object with a scalar `query`. Placeholders are expanded in SQL,
request pages, parameter names and values, referers, and assertions. SQL is
trusted local configuration and must never be derived from an HTTP request or
an LLM response.

Supported assertions are:

- `response_contains` and `response_not_contains`, each accepting a string or
  list of strings;
- `query` paired with `scalar_equals`, `scalar_not_equals`, `scalar_zero`,
  `scalar_nonzero`, or `scalar_contains`.

Use the response marker assertions for database-backed reads. Use scalar
queries for create, update, and delete postconditions. Non-CRUD repairs simply
omit a matching rule and retain response validation.

Every repair validation JSON records whether the database oracle was applied,
the rendered setup SQL, sanitized request parameters, response metadata,
verification query, observed scalar value, individual assertions, and restore
errors. Parameters with password, secret, or API-key-like names are redacted.
