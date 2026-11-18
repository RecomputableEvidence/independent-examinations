# Receipt comparison dimensions v0.2 — proposed descriptive successor

**Scope:** add independently auditable comparison dimensions to `tools/compare_receipts.py`. This is a candidate interface, not an independently accepted model evaluation, correctness oracle, custody attestation, or operational permission.

## Compatibility and authoritative fields

The existing fields `disposition`, examination coordinates, `categories`, `disagreements_and_exceptions`, `external_authority_verified=false`, and `operational_admission=false` remain. The original mutually exclusive **primary categories** retain their precedence and meanings. New additive fields:

- `per_key_dimensions`: **every** compared `(case_id, arm)` in deterministic sorted order, including exact matches and missing rows; includes the primary category and independent dimensions. This makes dimension totals independently recomputable without relying solely on category summaries.
- `dimension_totals`: per-dimension counts using `true`, `false`, or `not_applicable` for Boolean fields; continuation values as named labels. For every dimension, total counts sum to `compared_keys`.

| Per-key dimension | Value and meaning |
| --- | --- |
| `cohort_equal` | Boolean when both rows exist; otherwise `null`. |
| `status_equal` | Boolean literal status equality when both rows exist, including two `EXCEPTION` statuses; otherwise `null`. |
| `reason_equal` | Boolean reason-string equality only when both rows are nonexception; otherwise `null` (even if both missing reasons are JSON null). |
| `exception_equal` | Boolean exception-text equality only when both rows are exceptional; otherwise `null`. |
| `left_has_exception` / `right_has_exception` | Boolean for a present row; `null` if that side has no row. |
| `continuation_relation` | For two nonexception rows, `BOTH_CONTINUE`, `LEFT_ONLY_CONTINUE`, `RIGHT_ONLY_CONTINUE`, or `NEITHER_CONTINUE`; otherwise `null`. |

`null` means **not applicable**, not false and not proof of agreement. `status_equal` and `reason_equal` are separate. Two matching exceptional statuses may have different exception texts. A cohort mismatch does not suppress any of these dimensions, although it continues to own the original primary category.

`RIGHT_ONLY_CONTINUE` and `LEFT_ONLY_CONTINUE` describe nothing beyond one side returning the literal `CONTINUE` while the other returns a different **nonexception** status. They do **not** order `WITHHOLD`, `STOP`, or `UNRESOLVED` in safety, validity, or governing authority.

## Exact agreement versus exception-free equivalence

The existing `--strict-equivalence` switch means no reported discrepancy, missing observation, or exception. It is **not** bytewise receipt equality. Two identical exceptions remain `exception_outcome` and exit 1 in strict mode; in ordinary descriptive mode they produce a report and exit 0. The new `exception_equal` dimension distinguishes matching from different exception texts without promoting matching failures into ordinary agreements.

## Validation and schema-only limitation

The public `compare(left, right)` function must validate both complete receipts, not only command-line loaded files. The Python verifier's rule that `(case_id, arm)` must be unique within a receipt is a **normative semantic requirement**, separate from the published JSON Schema's structural contract. Standard JSON Schema `uniqueItems` does not express composite-key uniqueness for otherwise different row objects; satisfying that schema alone is insufficient. Do not silently overwrite duplicate observations in a dictionary. This contract does not assert general equivalence between schema-only and runtime validation.

For file input, use one size-bounded binary read from one opened handle (at most 8,000,001 bytes) followed by strict UTF-8 decoding. Reject excessive JSON nesting (greater than 64 levels), duplicate JSON fields, nonstandard constants, and numeric tokens as controlled invalid records. Neither reader bounds nor the formal schema are a complete security audit.

## Evidence custody remains separate

Matching declared `subject_sha256` strings proves only agreement among declarations' identifiers. This comparator neither fetches the actual subject nor recalculates its digest, authenticates issuer evidence, attributes reviewer identity, or independently establishes ground truth. A separate rights-cleared manifest verifier must bind exact subject bytes, governing contracts, inputs, tools, metadata, and examiner custody *before* stronger provenance claims. Until independently examined, that verifier is **NOT IMPLEMENTED / NOT VERIFIED** in this track.

**Claim ceiling:** `DESCRIPTIVE_COMPARISON_ONLY / HISTORICAL_PRIMARY_CATEGORIES_PRESERVED / EXTERNAL_AUTHORITY_NOT_VERIFIED / COMPARATIVE_EFFECTIVENESS_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD`.
