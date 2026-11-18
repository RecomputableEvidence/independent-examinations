# Contributing examination work

Contributions should improve the reliability or discriminatory power of the examination, without biasing the desired result.

## Submitting a new examination

1. Open a proposal identifying the subject, precise source version/hash, research question, target population, baseline arms, controls, scoring method, source of expected outcomes, and failure/abstention policy.
2. Specify who authored the candidate, reference truth, independent implementation, and judgments. Disclose model/platform reuse, communication, and shared code.
3. Include **both** supported-continuance and warranted-withholding controls; represent unknown truth explicitly. Do not treat missing evidence as verified falsehood.
4. Freeze inputs and implementations before evaluated results are revealed. Public deterministic checks and any held-out commitment should be separately dated and identified.
5. Supply per-case, per-arm, per-implementation receipts with status, reason, **and exception** outcomes. Distinguish registered challenges from post-freeze exploration.
6. Publish failure cases, exceptions, conflicting reviews, and null results. Adjudicate conflicts transparently; do not edit historical receipts.

### AI model participation

Before a model's judgment can be considered for a scored examination, attach the versioned [MPI-01/MPI-02 declaration](protocol/MODEL_PARTICIPATION_INVARIANTS_v0.1.md). Identify the precise model and the source of that identification; state competence and evidence access for the governed question; provide a concise, independently inspectable decision basis and express whether it is the model's own judgment. Unknown model identity, missing evidence, unsupported certainty, and abstentions must remain in the public record. Do not ask for hidden reasoning traces. The declaration requires independent identity/evidence review before qualification, even when its structure passes screening.

## Public safety / data rules

- Synthetic examples only until public-disclosure rights are verified; do not upload private repositories, sensitive case evidence, personal data, or credentials.
- Do not ask GitHub Actions to execute arbitrary submitted third-party binaries or network-dependent agents. CI is limited to the standard-library validation demonstration.
- All contributor code and documentation are proposals until reviewed. No external operational authority is conveyed by acceptance.
- A reusable source license and contribution terms require an explicit steward decision; public visibility does not itself grant reuse rights.

## Review standard

Examiners should submit evidence-backed findings even when they refute the project. Reviewers should challenge both permissive errors and false refusals. Preserve the result that the original experiment actually established.
