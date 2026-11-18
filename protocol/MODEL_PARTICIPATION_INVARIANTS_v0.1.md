# Model participation invariants v0.1 — proposed

**Scope:** admission of AI-model-generated judgments into a *scored* independent examination population. This contract is additional to the existing examination protocol; it does not retroactively alter or rescore frozen historical receipts. This proposed v0.1 is subject to independent review and versioned amendment.

## MPI-01 — Accurate model identity and informedness disclosure

**Rule:** a model must identify its provider and exact deployed model identifier **when actually disclosed**, specify the provenance of that identification, and state whether its competence and evidence access are sufficient for the particular governed question.

The model must never invent an identifier, a revision, or a capability claim to satisfy the gate. When the platform does not disclose the model, record `UNKNOWN` or unavailable identity and keep the contribution as a nonqualified observation. Distinguish task readiness from confidence in an answer. `READY` is a self-assessment, not independent evidence of competence; a high-confidence assertion is not an accuracy measurement.

A model declaring `LIMITED`, `UNABLE`, incomplete evidence, or material gaps must not present a definitive scored judgment as independently informed. `ABSTAIN` or `UNRESOLVED` may be an appropriate, retained response. Do not penalize honest abstention by silently relabeling it as an incorrect decision.

Identity sources are `PROVIDER_METADATA`, `EXECUTOR_METADATA`, `SYSTEM_DISCLOSED`, `SELF_REPORTED`, or `UNKNOWN`. An identity evidence reference is a *pointer* and may be fabricated or stale. A self-reported model name is never enough to authenticate its provenance. The formal checker cannot verify that a provider actually issued a claimed identity; an independent examiner must inspect the underlying run metadata, issuer provenance, and binding to the examined run.

## MPI-02 — Decision ownership with an auditable support path

**Rule:** a model must make a bounded judgment it explicitly adopts as its own assessment, rather than mirroring the most likely, socially preferred, majority, or leaked reference answer. It must identify the governing criteria and evidence on which the judgment depends, the factors that were decisive, unresolved counterevidence or limitations, and a concrete condition that would change the decision.

The required *decision account* is a concise, public-facing justification, **not** a complete internal reasoning trace. No private chain-of-thought, hidden prompts, proprietary model architecture, weights, or privileged deliberation is requested. Declared reasoning ownership is not independently provable from text alone; examiners should use blind, reference-controlled challenges and compare the decision with actual cited evidence. Factual rebuttal or newly authenticated evidence may warrant a correction, and such a correction must be retained rather than treated as disloyalty to the initial statement.

Each decisive link binds a specific registered rule reference, evidence reference, and short explanation of relevance. Free-floating favorable language is insufficient. A rule/evidence reference without resolution or independently inspectable content is a recorded claim, not proof that the content is valid.

## Two-stage participation disposition

1. **Formal screen:** `tools/check_model_participation.py` validates record structure and the minimum MPI-01/MPI-02 declarations. It may report `FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW`, `ABSTENTION_RETAINED_NOT_SCORED`, or `NOT_ELIGIBLE`. These are *screening* outcomes only.
2. **Independent examination:** a distinct examiner resolves model identity against provider/executor metadata, checks exact run and source binding, verifies actual evidence access, considers uncertainty and conflicts, and selects independent cases to challenge whether the model's stated support path predicts its decisions. Only a separately published adjudication may designate the submission eligible for the scored cohort.

Neither stage grants workflow execution permission, source sealing, external issuer status, operational admission, or comparative superiority. Passing the first stage must **never** automatically set `qualified_for_scored_examination = true`.

## Minimum declaration coordinates

`experiment_id`, `subject_sha256`, `case_id`, `arm`, `run_id`; model identity and identity source; capability readiness and evidence access; decision/abstention status, ownership declaration, governing rule and evidence references, short decisive links, explicit limitations, and a changed-decision condition.

Reference labels are synthetic in demonstrations. No claim about real model identity or external authorization follows from a syntactically valid receipt.

## Required controls for examination

- Exact disclosed model ID vs omitted, guessed, or mismatched ID.
- Provider/executor metadata present vs bare self-report vs contradictory witness.
- `READY` with sufficient identified evidence vs `LIMITED`/`UNABLE` or admitted gaps.
- Original evidence-linked judgment vs repeated expected answer with no decisive support.
- Defensible conclusion vs unsupported confident conclusion; legitimate abstention vs fabricated certainty.
- Supported change of decision after new evidence vs unjustified answer-shifting to match a favored result.

**Claim ceiling:** `MODEL_PARTICIPATION_INVARIANTS_PROPOSED / FORMAL_SCREEN_ONLY / INDEPENDENT_IDENTITY_AND_DECISION_QUALIFICATION_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD`.
