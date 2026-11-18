# MPI PR #2 input-boundary repair 003 — proposed successor

**State:** `BOUNDED_BUILDER_REPAIR / TESTED_LOCALLY / INDEPENDENT_SUCCESSOR_REVIEW_PENDING / NOT_QUALIFIED`

## Frozen history and examination trigger

- Original participation candidate PR #2: `90b54ee3970d2e1e2520ee8b4b0ea3a6c36b383b`, checker Git blob `382c92b7452b836cdcdb8154cf249bbf712a40a2`.
- Design-only MPI-QUAL-001 PR #3: `537218d2b2434733bf934819e9ae0c2e563750c4`; no live model cases run or adjudicated.
- Local examination: `MPI-QUAL-001-EXAM-001`, 2026-11-18; 50/50 frozen PR #2 tests and 2/2 design tests on both CPython 3.12.14 and 3.13.5. The examination's separate shadow analogues are *not* registered live model qualification.
- Newly reproduced F-01: direct-call `schema_version` can be a non-JSON object whose `__eq__` claims equality to `"0.1"`. `validate_participation()` accepts it; `screen_participation()` fails with uncontrolled `TypeError` while hashing.
- Newly reproduced F-02: `load_record()` uses pre-read `stat().st_size` to enforce 250,000 bytes. A POSIX FIFO reporting size zero supplies 250,001 bytes and is accepted.

## Narrow changes

1. **F-01:** Require exact built-in string type for `schema_version`, then exact `"0.1"` value. Convert the constructed direct-call counterexample into a controlled `ParticipationError`.
2. **F-02:** Reject nonregular input paths before opening; retain the preliminary size check as an optimization but also limit binary reading to `MAX_BYTES + 1` and reject oversized actual reads. Decode accepted bytes as UTF-8 for the unchanged depth and JSON parser.
3. Set public checker-version marker to `MPI_SCREEN_0.1.3`; preserve the valid-declaration hash profile, field names, qualifications all false, and abstention semantics.
4. Add four regression methods covering the F-01 equality trick, exact byte boundary, lying pre-open stat size, and FIFO rejection including controlled CLI exit 2.

## Verification and bounded claim

Builder-side executed on reconstructed pinned candidate plus only the stated source, test, protocol, README and this finding record:

| Runtime | Complete repository tests | New test methods |
| --- | --- | --- |
| CPython 3.12.14 | **54/54 passed** | 4 |
| CPython 3.13.5 | **54/54 passed** | 4 |

The synthetic valid example's declaration digest remains `701326610d0fbbb592e952cf13435b006c42cbe59fe124d717189b7c390729f3`. The version field intentionally differs from the preceding output.

A separately scripted **7,200-declaration synthetic predecessor/successor differential** ran on both interpreters. Every complete report matched **after excluding only the intentionally changed `checker_version` field**. Each run returned 2,880 retained abstentions, 4,311 ineligible and nine pending formal review; all authentication, qualification and admission flags remained false. Reproduce using `python3 tools/verify_mpi_repair_003.py --predecessor /path/to/frozen_PR2_checker.py`, after independently obtaining the exact predecessor file (the script checks its frozen Git blob SHA-1). This matrix tests finite declared-input compatibility, not external truth, model effectiveness, or an independently blinded oracle.

**Not established:** source or run authentication; safety against all special-file races, arbitrary custom Python objects, hostile concurrent writes, model identity truth, decision ownership, comparative AI effectiveness, independent reviewer acceptance, or operational admission. PR #2 and PR #3 frozen commits remain historical examination coordinates. This repair is a candidate for adverse review, **not** a merge or admission decision.
