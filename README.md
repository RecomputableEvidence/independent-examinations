# Independent Examinations

An open, outcome-neutral framework for independently reproducible, cross-platform examinations of AI systems, evidence, authorization, and justified continuance.

**Status: infrastructure draft / no qualified system / no operational admission.** This repository records what an examination establishes **and** what it cannot establish. It is not an issuer, certification authority, security approval, or deployment gate.

## Founding principle

> Examine to discover what the evidence establishes—not to validate what we hope is true.

The examined system does not set its own success criteria. Favorable, adverse, discrepant, inconclusive, and unscorable observations are retained without rewriting historical experiments.

Read [CHARTER.md](CHARTER.md), [CLAIM_BOUNDARIES.md](CLAIM_BOUNDARIES.md), and the [examination protocol](protocol/EXAMINATION_CONTRACT_v0.1.md) before contributing.

## First registered research candidate

[NGAST-RELATIONAL-CONTINUANCE-COMP-004](experiments/NGAST-RELATIONAL-CONTINUANCE-COMP-004/PREREGISTRATION.md) proposes two **separately examined** work packages:

- **R1 — Reviewer type-contract repair:** exact candidate/reviewer status, reason, and exception comparison across all four arms. Historical COMP-003 remains unchanged.
- **R2 — Case-bound relational semantics:** a governing semantic contract fixed outside candidate-supplied graph declarations, including temporal consequence boundaries.

Neither work package is reported as implemented, source-frozen, or independently qualified here. Historical COMP-001/002/003 artifacts are **not republished** pending source-rights, disclosure, and custody review.

## Reproducible infrastructure demonstration

`tools/compare_receipts.py` compares two standardized examination receipts without treating either as a truth oracle. It is a **receipt agreement tool**, not a classifier, evaluator of real authorization, or method-effectiveness benchmark.

Requirements: Python 3.10+ standard library only.

```bash
python3 -m unittest discover -s tests -v
python3 tools/compare_receipts.py examples/left.json examples/right.json
```

The second command deliberately reports discrepancies. An ordinary result with discrepancies is **not** an unsuccessful tool invocation; suppressing disagreements would defeat the purpose.

## Contribution model

1. Preregister the question, subjects, controls, scoring rules, and unknowns before outcome disclosure.
2. Freeze and identify the exact executable source, inputs, and governing contract with hashes.
3. Record separately authored examiner outputs and their environment/version identifiers.
4. Publish differences, exceptions, and positive-control behavior; do not call agreement with an implementation independent truth.
5. Seek review and adjudication before making a comparative or external qualification claim.

See [CONTRIBUTING.md](CONTRIBUTING.md). Open pull requests are proposals, **not** admission or independent acceptance.
