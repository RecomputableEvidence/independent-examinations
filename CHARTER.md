# Founding charter — v0.1 (proposed)

## Purpose

Determine what examined systems demonstrably do, under which conditions, and with which limitations. Examination design must neither favor nor disfavor NGAST, Fork/REBS, any vendor, method, baseline, or examiner.

## Constitutional constraints

1. **Symmetry:** preserve supported continuance, warranted refusal, adverse outcomes, false refusals, disagreements, crashes, and unresolved observations on equal evidentiary terms.
2. **No self-certification:** the implementation under examination cannot supply the sole governing oracle for its correctness. The builder's provisional expectations remain labeled provisional.
3. **Separation of layers:** computational reproduction, formal conformance, independent ground truth, external authority, comparative method effectiveness, and operational admission are different claims.
4. **Precommitment:** preregister cases/sampling, arms, reference sources, scores, exclusion rules, and stop conditions before examining candidate outputs. Amendments become versioned successors, not silent edits.
5. **Independence disclosure:** name the author(s) of cases, implementations, examiners, judges, and custodians; identify shared dependencies or assistance. Multiple model/platform outputs are not automatically independent truth.
6. **Fair comparison:** align evidence access, context, computation, pass count, and adjudication resources across arms; report material imbalances.
7. **Blindness where feasible:** preregister public protocols while an independent custodian may hold unreleased cases under a commitment; disclose the cases and commitment check after testing. A published test set alone is vulnerable to overfitting.
8. **Preservation:** never overwrite historical frozen inputs, outputs, adverse findings, or previously failed candidates. Later corrections have their own identifiers and evidence lineage.
9. **Authority boundary:** examination does not issue credentials, authorize an action, revoke rights, approve integration/deployment, or grant operational admission.
10. **Publication boundary:** do not post real credentials, regulated/private information, or non-public third-party source without verified disclosure rights.

## Required model-participation invariants

The [model participation contract](protocol/MODEL_PARTICIPATION_INVARIANTS_v0.1.md) governs AI model contributions to scored examinations.

- **MPI-01 — Identity and informedness.** A model must state its identity accurately to the extent actually disclosed, the basis for that identity claim, and whether it can make an informed assessment of the **specific** governed matter. A model must abstain or disclose uncertainty when required evidence or competence is absent. Identity and confidence claims are not proof of accuracy; independently authenticated run metadata remains necessary for scored qualification.
- **MPI-02 — Decision ownership and evidence path.** A model must take responsibility for the conclusion it submits within a stated scope, distinguish its own judgment from repetition of an expected answer, and provide an inspectable summary of governing criteria, relied-upon evidence, decisive factors, uncertainties, and conditions that would change the result. No private chain-of-thought, model weights, or proprietary reasoning trace is required or requested. Revising a decision when new evidence warrants it is responsible conduct, not a violation.

Submissions not meeting both invariants may be retained as unqualified observations but cannot silently enter scored independent-comparison populations. Passing syntactic checks does not establish that either self-declaration is authentic or correct.

## Examiner roles

- **Candidate author:** submits a bounded, identified implementation and records known limitations.
- **Contract steward:** freezes the normative requirements and scoring contract before candidate execution.
- **Case and evidence custodian:** establishes case truth independently where possible, marks unsupported cases unscorable, and preserves held-out commitments.
- **Examiner:** reconstructs source and executes an independently implemented or independently controlled assessment; discloses dependencies.
- **Adjudicator:** examines disagreements, including shared-error risks, without treating numerical majority as proof.

One individual/platform may fill multiple roles only with that overlap explicitly disclosed; independence claims must then be correspondingly narrowed.

## Acceptable outcomes

`SUPPORTED`, `ADVERSE`, `DISAGREEMENT`, `INCONCLUSIVE`, `UNSCORABLE`, and `NOT_RUN` are all publishable observations. These are **reporting categories**, not candidate authorization statuses. A `CONTINUE` candidate output never independently authorizes execution.
