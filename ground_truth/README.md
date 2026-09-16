# DRHL Ground-Truth Datasets

This directory contains the two independently reviewed ground-truth datasets
used by the DRHL evaluation. They are released together so that vulnerability
detection and access-control-code extraction can be audited separately.

| Dataset | Evaluation unit | Size | Entry point |
| --- | --- | ---: | --- |
| BAC vulnerabilities | One distinct authorization failure and protected operation | 50 records across 16 applications | [`ground_truth.csv`](ground_truth.csv) |
| Access-control snippets | One unique authorization parameter or validation function | 163 entities across 16 applications | [`access_control_snippets/entities.csv`](access_control_snippets/entities.csv) |

The access-control dataset contains 140 unique parameters and 23 unique
functions. Its per-application JSON files retain 142 parameter annotation
occurrences because two AWCM parameters are annotated in more than one source
context. The consolidated CSV uses the unique semantic entity as its evaluation
unit and records the number of annotation occurrences.

## Directory layout

```text
ground_truth/
|-- README.md
|-- ground_truth.csv
|-- ground-truth_report.md
|-- ground-truth_comparison.tex
|-- vulnerabilities/
|   |-- README.md
|   `-- manifest.json
|-- audit/
|   |-- README.md
|   |-- <application>/audit_log.md
|   |-- <application>/evidence/
|   `-- tools/
`-- access_control_snippets/
    |-- README.md
    |-- manifest.json
    |-- entities.csv
    |-- build_index.py
    `-- applications/<application>/
        |-- parameters.json
        `-- functions.json
```

The vulnerability files remain at their existing top-level paths because the
audit utilities under `audit/tools/` refer to those stable locations. The
`vulnerabilities/` directory is an index and documentation layer; it does not
duplicate the 50-record CSV or the audit evidence.

## Independence from DRHL execution

Neither ground-truth dataset is loaded by the DRHL crawling, detection,
extraction, or repair pipeline. In particular, the access-control ground truth
is not supplied to either LLM repair stage and is not used to generate
`llm_snippets.json`. It is used only after extraction to calculate TP, FP, FN,
Precision, and Recall.

No file under `drhl/`, `configs/`, or `runs/` is generated from this directory.
Reorganizing these released datasets therefore does not change the main
experiment's behavior or artifacts.

## Dataset boundaries

- The vulnerability ground truth answers which concrete authorization
  failures exist and which unauthorized effects were independently confirmed.
- The access-control snippet ground truth answers which authentication,
  identity, role, permission, ownership, and validation entities should be
  recovered from each application's source code.
- Detection outputs and extracted snippets are predictions, not ground truth.
  They remain outside this directory and are compared with these datasets only
  during offline evaluation.

See [`vulnerabilities/README.md`](vulnerabilities/README.md) and
[`access_control_snippets/README.md`](access_control_snippets/README.md) for
the construction rules, schemas, and count definitions.
