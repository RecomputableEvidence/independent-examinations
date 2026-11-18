# COMPARATOR-REPAIR-001 — Neutral receipt comparison successor v0.2

**State:** `REGISTERED_CANDIDATE / LOCAL_REPLAY_PENDING / EXTERNAL_ACCEPTANCE_NOT_ESTABLISHED / NO_OPERATIONAL_ADMISSION`.

**Frozen historical reference:** public `main` commit `9a3427a8070f6032ff9dfcccba5e0dc21cfb1dab`, comparator Git blob `55d210f6c9aad00e32bbabe502870c78e328dd3d`. The original six-case example, fourteen comparator tests, and 225-cell external synthetic branch examination remain historical evidence; this repair is a separately reviewable successor, not a retroactive alteration of their claims.

## Objective and falsifiable acceptance criteria

Improve descriptive *auditability* without treating receipt agreement as truth, relative continuation as a general safety ranking, internal digest equality as custody, or an exception as a valid `WITHHOLD`. Preserve all prior primary categories, raw discrepancy records, and ordinary/strict CLI semantics while exposing separately recomputable comparison dimensions.

Predeclared acceptance checks (run against unchanged baseline fixtures as well as the repaired code):

| ID | Challenge | Expected bounded result |
| --- | --- | --- |
| C01 | Historical six-case example | Primary categories unchanged: 2 exact, 1 each right more permissive, right more restrictive, reason disagreement, exception |
| C02 | Historical 225-cell status/cohort cross-product | All classifications unchanged: 150 cohort, 27 exception, 18 decision, 12 exact, 9 permissive, 9 restrictive |
| C03 | Equal nonexception statuses and reasons | Exact agreement and all applicable equality flags true; included in per-key dimensions |
| C04 | Same exception status and exception text | Primary `exception_outcome`, equal exception-text flag, strict-equivalence exit 1 |
| C05 | Different exception texts | Primary `exception_outcome`, unequal exception-text flag; no promotion to success |
| C06 | Cohort and status/exception conflict simultaneously | Original primary `cohort_disagreement`, *both* underlying differences visible |
| C07 | CONTINUE vs other nonexception status | Right/left continuation relation explicit; no ordering asserted among STOP/WITHHOLD/UNRESOLVED |
| C08 | Missing row on either side | Missing category preserved; unavailable comparison dimensions marked not applicable |
| C09 | Repeated case/arm passed directly to `compare()` | Controlled `ReceiptError`, no silent dictionary overwrite |
| C10 | Schema-valid structure with repeated case/arm key | Python normative duplicate validation enforced and its schema-only limitation documented |
| C11 | Excess-length receipt or excessive nesting | Controlled validation error, not unbounded file read or crash |
| C12 | Oversized integer or nonstandard JSON constant | Controlled invalid-record error; never a decision outcome |
| C13 | Different subject digests or experiment identifiers | Refuse comparison; do not infer that equal declared digest strings attest input custody |
| C14 | Independently reconstructed orthogonal totals | Every total recomputable from a per-key record; exact original categories remain comparable |

## Contract boundaries

- Primary categories remain mutually exclusive and backward-compatible. Orthogonal dimensions are **additional observations**, not competing truth labels.
- Boolean `cohort_equal` and `status_equal` compare present rows. `reason_equal` is not applicable when either row is exceptional. `exception_equal` compares texts only if both rows are exceptional. Missing sides are not silently treated as equal.
- `continuation_relation` refers strictly to one/both/neither `CONTINUE` in nonexception pairs; it makes no judgment about the relative authority or safety of other statuses.
- Strict equivalence continues to mean **exception-free status-and-reason agreement with matched cohorts and keys**, not literal bytewise receipt identity. Two identical exceptions still fail strict mode.
- `subject_sha256` continues to be a caller-supplied identifier checked for format and equality, **not** an independently recomputed source digest. Artifact custody and provenance are a separate future manifest-verifier track, not an implied outcome of this repair.
- Schema validation cannot, in the published standard schema, express `(case_id, arm)` composite uniqueness; the runtime verifier's check is an additional normative requirement.
- Input controls bound one read and depth, but do not certify resource security, platform independence, examiner independence, or correctness.

## Required examination packet and disposition

Retain pinned original source, original examples, registered case matrix (or its exact generator and seed), repaired source and tests, interpreter version, both primary and multidimensional reports, divergence list, and exception logs. Do not reuse builder generated expected results as the *only* oracle; the independent reviewer must implement or recompute the added dimensions separately and introduce unregistered adverse inputs.

Any unexpected primary-category change, exception swallowed as a decision, unbounded error, missing artifact, or false external-authority/admission field is an adverse finding. Record it and retain the draft unmerged pending independent examination.

**Claim ceiling:** `COMPARATOR_REPAIR_LOCAL_CANDIDATE / SOURCE_CUSTODY_UNATTESTED / NO_TRUTH_ORACLE / COMPARATIVE_EFFECTIVENESS_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD`.
