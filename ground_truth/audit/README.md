# Ground-Truth Verification (Independent Manual Audit)

This directory contains the artifacts of the independent manual audit that
established the per-vulnerability ground truth released in
`ground_truth/ground_truth.csv` and described in Section 5.1 (Ground-Truth
Construction) of the paper.

The audit follows the three-step procedure of Section 5.1:

1. **Independent auditing and authorization analysis.** Two authors
   independently audited each benchmark application's source code and
   executable workflows **without consulting DRHL's detection outputs**.
   They enumerated requestable endpoints and security-sensitive operations -
   protected-resource access as well as state-changing operations such as
   creation, modification, deletion, and administrative actions - and, for
   each operation, determined the expected authorization requirement from the
   application's role checks, identity and resource-ownership constraints,
   surrounding access-control logic, and normal application behavior.
2. **Uniform vulnerability validation.** Unauthorized test cases were
   constructed by replacing the legitimate subject with a user that does not
   satisfy the corresponding authorization requirement, and were executed
   against the local deployments. A candidate was included in the ground
   truth only when the unauthorized operation actually succeeded: for
   resource-access operations the attacking actor obtained the protected
   resource or content; for state-changing operations the unauthorized effect
   was confirmed in the application or database state. Test cases that were
   properly denied are recorded as such (examined, not vulnerabilities).
3. **Cross-checking and disagreement resolution.** The two auditors'
   candidate sets and supporting evidence were cross-checked; disagreements
   were independently reviewed by a third author and the final label was
   determined by consensus.

The ground-truth set was finalized **before comparison with DRHL's detection
reports**, so any ground-truth vulnerability not reported by DRHL is counted
as a false negative.

## Directory layout

```text
audit/
  README.md                     this file
  tools/                        executable tooling (read-only with respect to DRHL)
    verifier.py                 token-marker validation harness (DB + replay + recording)
    verify_<app>.py             per-application validation drivers
    generate_audit_logs.py      generates audits/<app>/audit_log.md
    generate_gt_table.py        generates ground_truth/ground-truth_report.md (50 records)
    update_csv.py               applies validation results to ground_truth.csv
  audits/
    <app>/
      audit_log.md              complete per-application audit log (three-step procedure)
      evidence/
        GT-xxx.json             per-record validation experiment (steps, SQL, verdicts)
        GT-xxx_*.html           archived response bodies
        baseline.sql            database baseline snapshot used for restore verification
        summary.json            per-app summary incl. per-record restore verification
```

The human-readable table of all 50 ground-truth records lives at
`ground_truth/ground-truth_report.md`.

## Validation method (token markers)

Selected by operation type:

- **Read (resource access)**: a unique marker token is injected into a
  protected database field; the replay must expose the token in the response.
- **Create**: the replay carries a token; a new row containing the token must
  appear in the database.
- **Delete**: a token row is inserted first; the replay must remove it.
- **Update**: token1 is written first; the replay carrying token2 must change
  the stored value to token2.

All tokens follow the `DRHLGT_<label>_<timestamp>` pattern. The database
baseline is restored and verified after every single record, and application
files touched by validation are restored as well.

## Status

- Validated and documented: AWCMs (5), Phpoll (3), Phpns (7), bWAPP (5),
  DVWA (3), SCARF (3), EventsLister (2), MyBB (1), Wackopicko (2),
  Jspblog (7), JsForum (6), jwablogger (1), DjangoBlog (1),
  django_lms (1), BBS_Pro (1), orangeforum (2) - 50 records.
- All 50 records are validated and documented.
