# MPI-QUAL-001 — independent evidence intake (proposed v0.1)

**State:** `PREPARATION_ONLY / NO_AUTHENTICATED_RUN / NO_ADJUDICATED_CASE / NO_QUALIFICATION / NO_OPERATIONAL_ADMISSION`

This is a successor *preparation tool* for the frozen design-only
[MPI-QUAL-001 registration](PREREGISTRATION.md) and
[12-case registry](CASE_REGISTRY.json). It does **not** amend the registered
cases or their conditional expected gates. The exact PR #2 checker candidate
remains `90b54ee3970d2e1e2520ee8b4b0ea3a6c36b383b`; this intake
has no model runtime or independent provider metadata.

## Objective

Before comparing multiple AI platforms, obtain enough independently
identified *governing truth* and *run identity evidence* that favorable,
unfavorable, revised, abstaining, and exceptional decisions can be
distinguished without rewarding mere agreement with a preferred answer.

This preflight tool intentionally answers only: **Which local evidence bytes
were supplied, did they match declared SHA-256 hashes, and which required
evidence categories are still absent?** It cannot authenticate a provider,
examine causal reasoning, infer hidden chain-of-thought, verify issuer
permission, or issue a scored qualification.

## Evidence classes and custody

Each supplied artifact is a file under a dedicated local bundle root, with an
ID, role, case coordinate (when applicable), exact relative path, SHA-256
digest, claimed acquisition origin, rights status, and a witness-reference
pointer. Every origin or witness field is **declarative metadata** until an
independent examiner corroborates it.

| Moment | Minimum material to prepare | Who must establish it |
| --- | --- | --- |
| Before candidate exposure | Frozen candidate/source, independently authored examiner harness, rights/disclosure record | Independent examiner / rights holder |
| Before each registered case | Governing contract, admissible evidence snapshot, independently held case truth, blinded reference answer | Independent fixture adjudicator outside the candidate |
| During/after each model run | Actual model prompt/input, unedited output, its public decision declaration, provider/executor run metadata | Run executor and independent metadata witness |
| Before scoring | Exact run-to-input/output binding; reference and issuer resolution; correction and exception history; review of leakage and shared dependencies | Separate adjudicator, not merely the candidate or the preflight script |

Do not expose the blinded answer reference to participating models or their
answer-construction tools. Do not publish model provider secrets, privileged
user data, confidential governing contracts, or hidden reasoning. A
`RESTRICTED` artifact may be verified in a protected examination environment
without being posted publicly. Public evidence summaries must not imply that
withheld bytes have been independently accessed by everyone.

The 12 registered cases must include positive controls (D01, D05), adverse
controls including a changed/revoked grant (D04), and retained abstention
(D06). A consistently refusing model cannot satisfy selective authorization
discrimination solely by avoiding false continuance.

## Recording and preflight

1. Copy `INTAKE_MANIFEST_TEMPLATE.json` into an examiner-controlled bundle
   as `manifest.json`, keeping the original template unchanged.
2. Obtain actual rights-cleared evidence. Place each file beneath that
   bundle's root and record its digest, role, `case_id`, acquisition class,
   and external witness pointer. Never fabricate missing evidence to get a
   green result. Use `UNKNOWN` where a provider withholds a model build ID.
3. Declare each actual model run with its exact `run_id`, registered case ID,
   claimed model identifier, and artifact IDs for metadata, input, output,
   and public declaration. The preflight inventories whether at least two
   distinct non-`UNKNOWN` **claimed** model identities occur per registered case; this is
   only comparative coverage and does not authenticate different providers,
   implementations, or reasoning independence. Unknown run identity remains
   unscored.
4. Run:

   ```bash
   python3 tools/verify_mpi_intake.py /absolute/bundle/root/manifest.json --bundle-root /absolute/bundle/root
   ```

   Exit 0 indicates **only** that the manifest was syntactically processed.
   Exit 1 means evidence is incomplete or a digest differs. Exit 2 means the
   manifest itself is invalid. Structured output retains all missing/different
   artifacts. No preflight exit code is qualification or authority.
5. Securely transfer the immutable inputs and receipts to independently
   accountable reviewers, have them recompute digests and source provenance,
   then conduct the *preregistered* blind case examinations. Keep every
   conflicting observation, correction, and exclusion visible.

The preflight records at most 32 MiB per referenced file; larger source
artifacts need a separately versioned custody route. The verifier refuses
path traversal, absolute artifact paths, and symbolic links. It reads local
files only and does not contact providers. It does not establish atomic
filesystem snapshot custody or protect its own output from later alteration.

## Gates and stops

- **Q0:** Source/fixture **custody remains blocked** until an external
  examiner verifies the actual governing inputs and reference truth.
- **Q1:** Model identity/informedness **remains unverified** until provider
  or executor metadata is independently bound to each recorded run.
- **Q2:** A public support account is inspectable but **not proven causal**;
  check source resolution, favorable/adverse changes and leakage under blind
  challenge rather than asking for private chain-of-thought.
- **Q3:** Scored qualification and comparative metrics **remain withheld**
  until a separate adjudicator establishes Q0–Q2 and the true case outcomes.

No artifact names, model claims, status values, or matching hashes can set an
authority/qualification boolean true. In particular, a candidate-written
`PROVIDER_OBTAINED` string or a self-supplied `witness_ref` is never
authentication by itself.
