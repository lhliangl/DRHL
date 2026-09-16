# Access-Control Code-Snippet Ground Truth

This dataset contains the manually reviewed access-control entities used to
evaluate DRHL's access-control code extraction. It covers the same 16
applications as the vulnerability ground truth and represents the two semantic
components from which access-control snippets are formed:

- authorization parameters: authentication state, current identity, roles,
  permissions, ownership values, account status, and policy flags;
- validation functions: functions, methods, decorators, middleware, or
  handlers whose control flow performs an access-control decision.

The per-application JSON records preserve source files, entity kinds, source
classes, line spans when available, and the manual-review rationale. They are
the ground truth for semantic snippet extraction; complete application source
files are intentionally not duplicated here.

## Construction and inclusion rules

The annotations were produced through manual source review using a
better-to-miss-than-wrong principle. An entity is included only when its source
context shows that it contributes to authentication, identity recovery,
authorization, role or permission evaluation, ownership comparison, or denial
control flow.

The following are excluded unless they directly participate in an
access-control decision: login credentials, CSRF tokens, redirect parameters,
ordinary content values, UI preferences, general input validators, routing
variables, and CRUD wrappers.

## Files

- [`manifest.json`](manifest.json): provenance, scope, and counts.
- [`entities.csv`](entities.csv): consolidated unique-entity index for all 16
  applications.
- `applications/<application>/parameters.json`: manually reviewed parameter
  annotation occurrences.
- `applications/<application>/functions.json`: manually reviewed validation
  functions and source spans.
- [`build_index.py`](build_index.py): deterministic utility that rebuilds only
  `entities.csv` from the adjacent JSON annotations.

## Count semantics

Two count levels are deliberately reported:

1. Annotation occurrences preserve distinct reviewed source contexts. There
   are 142 parameter occurrences and 23 function occurrences.
2. Evaluation units deduplicate names within each application using the same
   case-insensitive, whitespace-insensitive normalization as the extraction
   evaluation. There are 140 unique parameters and 23 unique functions, for
   163 evaluated entities in total.

The two duplicated parameter names are AWCM entities annotated in more than
one source context. The consolidated CSV merges their paths and rationales and
retains the number of occurrences in `Annotation Occurrences`.

## JSON fields

Common fields include:

- `app` and `language`: application and language family.
- `reviewed_at`, `method`, and `principle`: annotation provenance.
- `name`: semantic parameter or function name.
- `kind`: identity, role, permission, status, middleware, role check, or other
  access-control role played by the entity.
- `source`: origin class for parameters, when applicable.
- `files` or `file`: reviewed source location.
- `start_line` and `end_line`: reviewed function span when available.
- `rationale`: why the entity belongs to the access-control ground truth.

Some retained source paths reflect the local deployment used for the manual
audit. They are provenance hints only; neither DRHL nor the index builder uses
them to locate runtime source code.

## Rebuilding the consolidated index

From the repository root:

```powershell
python ground_truth\access_control_snippets\build_index.py
```

The builder validates that the resulting index contains exactly 140 unique
parameters and 23 unique functions.

## Isolation and leakage prevention

This dataset is not an input to DRHL extraction or repair. It is never added to
`llm_snippets.json`, the first-stage repair prompt, or the second-stage repair
prompt. Predictions are generated without these annotations, and the ground
truth is consulted only afterward to compute TP, FP, FN, Precision, and
Recall.

The JSON snapshot was consolidated from the latest manually reviewed labels
previously stored under `test_extract_dracv/ground_truth`. That isolated
experiment retains its own copy for reproducibility; this directory is the
released, centrally documented ground-truth view.
