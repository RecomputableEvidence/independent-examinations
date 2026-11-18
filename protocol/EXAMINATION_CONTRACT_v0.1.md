# Independent examination contract v0.1 — proposed

This is a **format and governance proposal**, not a sealed or executed experimental contract.

## Examination object

Each experiment registers `experiment_id`, `protocol_version`, target source archive digest, case-set digest, expected-outcome authority, arms, sample strategy, controls, resource parity, stop rules, and a permitted claim ceiling. Tests whose truth cannot be established independently of the candidate are tagged `UNSCORABLE`, never relabeled to make the metric complete.

## Minimum immutable evidence coordinates

- Subject: exact source commit/archive SHA-256, toolchain and execution image ID, with source-rights check.
- Case: `case_id`, frozen input checksum, independent truth/contract version, preregistered or exploratory flag.
- Execution: platform, implementation identity, run ID, method configuration, environment version, input digest, observed status/reason/exception.
- Custody: author, examiner, custodian, timestamp and any postfreeze modifications, plus signed/externally mirrored references where available.

Hash equality establishes byte consistency only. It does not authenticate who originally created the bytes or when.

## Examination stages

1. **Registration** — publish neutral question, designed controls and outcomes eligible for comparison, authorship/conflicts, criteria, and limitations.
2. **Freeze** — record exact source and inputs, including an independently held challenge commitment when used.
3. **Reconstruction** — verify manifest membership, hashes, schema, implementation identity, and runnable environment.
4. **Execution** — each examiner performs a distinct replay and/or source review, preserving results and exceptions.
5. **Differential examination** — identify missing cases, status disagreements, reason differences, crashes, false refusals and false continuations **only relative to established reference truth**.
6. **Adjudication** — publish all open exceptions, review conflicts, reference gaps, and stop conditions before any positive claim.
7. **Preservation** — freeze receipts and report with claim ceiling; changes create a versioned successor.

## Outcome categories

`CONTINUE`, `WITHHOLD`, `STOP`, `UNRESOLVED` are candidate decisions inside a named synthetic contract. `EXCEPTION` is a separate execution outcome, never a synonym for `WITHHOLD`. `SUPPORTED` or `ADVERSE` are examiner conclusions and require documented reference evidence. The neutral comparator records agreement without declaring correctness.

## Comparable effectiveness

Use matched cases, a registered reference independent of arm output, equivalent computational attention and access, and separate denominators for supported continuation, warranted withholding, unknown cases, and crashes. Report candidate behavior, reviewer agreement, and truth-relative performance independently. Genuine method superiority requires authentic source-frozen method execution and appropriately independent outcomes.
