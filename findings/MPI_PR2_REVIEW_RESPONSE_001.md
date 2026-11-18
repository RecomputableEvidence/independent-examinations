# MPI PR #2 independent review — repair candidate response 001

**Original reviewed head:** `29ef596d9f7129080572355ef0d24b125f6417a0` (preserved in Git history). **Scope:** formal model-participation declaration checker, not an actual model, external identity, issuer authorization, or governance decision.

**Received reviewer ZIP SHA-256:** `0b5064e12d32eb2b5f3560cb503f0de721c8826065f9125d0597fa1a25c40356`. Its supplied sources/results were examined as adverse inputs; the original archive was not modified or republished in this repository.

The outside reviewer independently ran 20 new tests and reported a 7,200-record selected-enum matrix: 2,880 abstentions retained, 4,311 not eligible, 9 pending review, and zero authority booleans true. These are **reviewer-reported** findings, not a new independent reexecution of that complete matrix in this repair.

The repair author separately executed the **same defined 7,200-combination matrix** locally after patching on Python 3.12.14 and reproduced those counts and zero authority booleans true. This is a local regression, not an independently chosen new examination. The complete local unit suite ran **45/45 PASS** (14 legacy receipt-comparator tests and 31 model-participation tests, including the original 20). The pre-repair failures were independently recreated locally before editing.

## Findings and bounded responses

| Finding | Original result, locally reproduced | Repair candidate | Standing |
| --- | --- | --- | --- |
| F1 unavailable identity variants | Padded `UNKNOWN` and lowercase `unknown` could pass formal screening. | Reject surrounding whitespace for provider/model/version; treat ASCII `UNKNOWN` case-insensitively, without changing real identifier case. | Implemented; independent reexamination pending |
| F2 standalone report binding | Changing subject digest, decision status, or identity reference left the entire report unchanged. | Include those fields, schema/checker version, and a defined whole-declaration parsed-JSON digest. Original input bytes are **not** cryptographically attested by this digest. | Implemented; independent reexamination pending |
| F3 missing limitations | Empty `counterevidence_or_limits` could pass on definitive decisions. | Require explicit nonempty limitation account for definitive decisions, without inventing contrary evidence; preserve abstention without such an account. | Implemented; independent reexamination pending |
| F4 JSON depth exception | 50,000 nested arrays below the byte limit caused an uncontrolled `RecursionError` exit 1. | Precheck maximum structural nesting and report invalid input with exit code 2; retain recursion-exception fallback. | Implemented; independent reexamination pending |

## Continued claim boundaries

- A model identity claimed in `EXECUTOR_METADATA` and an evidence-reference string may be invented; the screen does **not** independently authenticate either.
- A concise decision account does not prove derivation from the cited material, competence, explanation faithfulness, or correctness. Private chain-of-thought is not requested.
- Honest abstentions and abstentions with ownership flags are retained but not scored; retention does not authenticate intent.
- Git history preserves the original defective PR head. This candidate response does not retroactively rewrite its results.
- Earlier independent review findings against `tools/compare_receipts.py` (duplicate key parity, direct-call validation, multi-axis discrepancies, artifact custody) remain open and untouched.

**Disposition:** `MPI_FORMAL_SCREEN_REPAIR_CANDIDATE / INDEPENDENT_ACCEPTANCE_PENDING / SCORED_MODEL_QUALIFICATION_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD`.
