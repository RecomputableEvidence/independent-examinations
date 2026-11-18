# COMPARATOR-REPAIR-002 — Report snapshot integrity (v0.1)

**State:** `REPAIR_CANDIDATE / NOT_INDEPENDENTLY_ACCEPTED / PR4_HISTORICAL_REFERENCE_PRESERVED / NO_OPERATIONAL_ADMISSION`.

**Frozen examined predecessor:** draft PR #4 at `bdfb709fb5b9ee053cd7fff5b20394538fd5d1b0`, comparator Git blob `2d5d3249ece51f70f50ab05149d079a4926826e8`. Historical baseline `main` commit `9a3427a8070f6032ff9dfcccba5e0dc21cfb1dab`. The previous PR and all independent examination observations remain unmodified.

## Bounded defect and objective

A completed report's `disagreements_and_exceptions` currently refers to caller-owned row dictionaries. When a caller changes a row after comparison, the report's raw evidence changes while its per-key dimensions and totals remain the same. The goal is to make the report a **snapshot of validated comparison inputs**, not a live view of caller-owned containers.

Do **not** interpret this repair as proving source-byte custody, report authenticity, concurrent mutation safety, independent decision correctness, or external authority.

## Predeclared regression controls

| ID | Challenge | Required bounded outcome |
| --- | --- | --- |
| S01 | Valid `CONTINUE` vs `STOP` mismatch, mutate left reason after comparison | Existing report's left reason remains original; calculated `reason_equal` remains internally consistent |
| S02 | Change caller-owned status, cohort and exception text after comparison | Existing report's raw discrepancy and all stored dimensions/totals remain unchanged |
| S03 | Mutate both caller inputs, then compare again | New report reflects new valid inputs; old report remains unchanged |
| S04 | Missing observation on one side, mutate its present row | Retained present-row evidence is a snapshot; absent side remains `null` |
| S05 | Original historical six-case example | Existing primary categories and orthogonal dimensions unchanged |
| S06 | Historical 225 status/cohort cross-product | All 225 primary classifications and dimension sums unchanged |
| S07 | Direct-call malformed receipt or exception | Existing controlled validation and explicit exception semantics unchanged |
| S08 | Normal and strict CLI | Exit policies and JSON wire fields unchanged |

## Ownership semantics

`compare()` must validate both receipts and copy each schema-constrained observation before classification. Schema v0.1 row values are immutable Python `str` or `None`, so a fresh dictionary per row is sufficient to break the caller's mutable-row alias without a general-purpose object traversal. The returned report itself remains an ordinary mutable Python mapping; callers seeking archival immutability must serialize and bind its bytes separately.

**No guarantee of atomic snapshots under concurrent mutation of inputs during `compare()` is introduced.** The CLI's inputs remain in-memory parsed receipts, and no source seal, cryptographic signature, reviewer independence, or operational admission follows.

## Independent examination requirements

The external reviewer should independently derive the mutation-after-comparison oracle, reproduce the predecessor's counterexample before examining the repair, run the unchanged historical tests and examples, then challenge the repaired implementation using separately selected object-alias and exception probes. Preserve differing results, errors, and reviewer limitations. Independent acceptance and merge remain withheld.

**Claim ceiling:** `LOCAL_REPAIR_ONLY / HISTORICAL_RESULT_PRESERVED / INDEPENDENT_ACCEPTANCE_PENDING / EXTERNAL_AUTHORITY_NOT_VERIFIED / OPERATIONAL_ADMISSION_WITHHELD`.
