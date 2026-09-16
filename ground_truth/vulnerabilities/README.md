# BAC Vulnerability Ground Truth

This dataset contains the per-vulnerability ground-truth table used for the 16
benchmark applications in the DRHL evaluation. The canonical table is
[`../ground_truth.csv`](../ground_truth.csv), containing 50 BAC vulnerability
records. Repeated executions of the same protected operation under different
attacking accounts, concrete identifiers, or equivalent URL parameter values
are represented by one record. Distinct authorization failures at the same
endpoint, such as vertical and horizontal privilege escalation or update and
delete operations with different security effects, remain separate records.

## Independent construction principle

Ground-truth membership is determined from the application's expected
authorization policy and the observed effect of an unauthorized operation. A
DRHL label, HTTP 200 response, generated patch, or successful repair is not by
itself sufficient to establish ground truth. The expected policy is derived
from application roles, authenticated identity, resource ownership,
surrounding access-control logic, database relationships, and normal workflow.
Labels are finalized independently from comparison with DRHL's output so that
an established vulnerability omitted by DRHL can be counted as a false
negative.

## Uniform vulnerability criterion

A case qualifies as a BAC vulnerability only when both conditions hold:

1. The test actor does not satisfy the authorization requirement for the
   target resource or operation.
2. The unauthorized operation actually succeeds. For resource access, the
   actor obtains the protected resource or protected content. For creation,
   update, or deletion, the unauthorized state change is confirmed in the
   resulting application or database state.

A successful HTTP status without protected content, a public page, an invalid
or nonexistent object, an error page, a login page, or a denied request does
not satisfy this criterion. For a state-changing request, a success-looking
response or redirect is paired with a before/after state observation whenever
applicable.

## Files

- [`../ground_truth.csv`](../ground_truth.csv): canonical machine-readable
  table of 50 vulnerabilities.
- [`../ground-truth_report.md`](../ground-truth_report.md): human-readable
  per-record report.
- [`../ground-truth_comparison.tex`](../ground-truth_comparison.tex): released
  LaTeX comparison table.
- [`../audit/`](../audit/): per-application audit logs, replay evidence,
  database snapshots, and audit utilities.
- [`manifest.json`](manifest.json): compact dataset counts and stable path
  index.

## CSV fields

- `ID`: stable unique identifier for one ground-truth vulnerability.
- `Application`: benchmark application containing the vulnerability.
- `BAC Type`: `VPE` for vertical privilege escalation and `HPE` for horizontal
  privilege escalation.
- `Endpoint / Operation`: endpoint and, when needed, the security-sensitive
  action represented by the record.
- `Operation Type`: security-relevant effect, such as resource access,
  creation, update, deletion, or an administrative action.
- `Expected Authorization Requirement`: role, authentication, ownership, or
  application-specific condition that a legitimate actor must satisfy.
- `Unauthorized Test Case`: actor and request manipulation used to violate the
  expected authorization requirement.
- `Supporting Evidence`: retained evidence that the unauthorized actor
  obtained protected content or caused an unauthorized state change.

## Scope

The dataset contains 39 VPE and 11 HPE records. The application-level counts
are AWCMs 5, Phpoll 3, Phpns 7, Bwapp 5, DVWA 3, SCARF 3, EventsLister 2,
Mybb 1, Wackopicko 2, Jspblog 7, JsForum 6, jwablogger 1, DjangoBlog 1,
django_lms 1, BBS_Pro 1, and orangeforum 2.

This dataset is an offline evaluation artifact and is not read by the main
DRHL pipeline.
