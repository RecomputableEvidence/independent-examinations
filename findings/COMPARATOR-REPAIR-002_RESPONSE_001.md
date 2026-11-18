# COMPARATOR-REPAIR-002 — bounded response to external review

**Examined historical candidate:** draft PR #4 at `bdfb709fb5b9ee053cd7fff5b20394538fd5d1b0`, with comparator Git blob `2d5d3249ece51f70f50ab05149d079a4926826e8`.

**External examiner packet SHA-256:** `fa3b2fd68126f496c83e5ba48fadc185106c3819e604bdc230b73f09b561f8ce`. The examination source and supporting material were supplied separately and are **not** copied into this public successor. The reported source/package claims remain bounded by the examiner's self-disclosed model and environment limitations.

## Verified adverse finding

The external reviewer reported a mutable-input alias in the comparator's `disagreements_and_exceptions`: its `left`/`right` records referred directly to caller-owned row dictionaries, while per-key dimensions and totals were already computed. The repair author independently reproduced the behavior on the exact historical candidate before modifying source: changing the original left reason from `SAME` to `ALTERED_AFTER_COMPARE` changed the completed report's reason but left `reason_equal=true`.

This is a **library report consistency** problem. It is not evidence of a mistaken original classification at comparison time, an independently demonstrated CLI exploit, general model error, external source forgery, or operational admission.

## Bounded candidate repair

The public `compare()` function already validates the exact row schema, containing only built-in strings and null values. Build maps from fresh copies of each validated row before deriving both dimensions and discrepancy details. This removes caller-owned mutable-row aliases from the completed report without changing categories, comparison semantics, or wire format.

Six added mutation regressions cover: later left-reason changes, both-side row edits, exception text changes, comparison of altered current input while retaining the old report, missing rows, and distinct row-container identity.

**Builder-side verification:** the original 14 comparator tests, 14 dimension tests, and six new snapshot tests pass together (**34/34**) on CPython 3.12.14 and 3.13.5. The historical six-case example and 225-case matrix are exercised by the unchanged predecessor tests. This is a finite local result, not independent acceptance of the new candidate.

## Preservation and outstanding examination

- PR #4 and its exact examined head remain a historical reference; this successor is a distinct draft branch and review object.
- An access-blocked Copilot examination has no result about candidate correctness. A **blind source-only packet pinned to the original PR #4 commit**, with neither the external review's answers nor this successor repair, permits an uncontaminated retry.
- Any AI model naming or confidence claim is a self-report until independently bound to provider/executor metadata; computational reproduction and scored model-participation qualification remain separate.
- The returned report remains a mutable ordinary mapping for its recipient. This patch does not promise immutability against consumer-side edits, concurrent input mutation during comparison, signed custody, truth, or operational permission.
- Artifact source custody and previously unresolved examination boundaries remain separate obligations.

**Disposition:** `REPORT_SNAPSHOT_REPAIR_LOCAL_PASS / ORIGINAL_FINDING_PRESERVED / INDEPENDENT_REEXAMINATION_PENDING / COMPARATIVE_EFFECTIVENESS_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD`.
