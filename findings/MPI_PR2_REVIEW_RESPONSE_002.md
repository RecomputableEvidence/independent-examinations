# MPI PR #2 — second independent adverse review response 002

**Independently reviewed predecessor:** `891b68b96a070a74eb371aae4d8deced77644fd2` (preserved in Git history). **Review packet SHA-256:** `c21ebe353029752630103612ffa144a2e0425575ddc79e06daa4fb88e245fb57`. The related reviewer note SHA-256 is `2b1aad671448ee36085cd6620ca65bab3218bd43a58d8512085911e885bab64f`. The external review was not posted to GitHub by its examiner; its original packet is not overwritten or republished here.

The examiner reported 45/45 passing repository tests, a newly specified 7,200-cell matrix (2,880 retained abstentions; 4,311 ineligible; 9 pending review; zero authority booleans true), seven valid digest encodings, and 23 report-binding substitutions. The matrix is finite and **not** proof of equivalence to an earlier reviewer's undisclosed matrix. The reviewer identified the following two additional failures, reproduced by the repair author on Python 3.12.14 before editing; the review itself used Python 3.13.5.

| Finding | Reproduced adverse result at predecessor | Bounded candidate correction | Standing |
| --- | --- | --- | --- |
| R1 — schema-valid lone surrogate | An escaped U+D800/U+DFFF in `decision.basis_summary` passed structural checks, then UTF-8 digest encoding raised `UnicodeEncodeError`, yielding exit 1 and traceback. A direct `screen_participation()` call raised the same exception. | Check every accepted text field for valid Unicode scalar values during validation. Reject lone surrogate values before hashing; preserve existing sorted-JSON UTF-8 digest representation. Decode valid escaped surrogate pairs as supplementary characters. Guard duplicate-key diagnostic rendering against unencodable characters. | Candidate implemented; independent reexamination pending. |
| R2 — oversized JSON integer | A 5,000-digit integer token in a 5,006-byte record caused decoder `ValueError` and exit 1, rather than controlled invalid-record exit 2. | Reject `parse_int` and `parse_float` tokens during JSON parsing because no numeric field exists. Retain duplicate-field and nonstandard-constant rejection. Do not raise the interpreter's numeric conversion limit. | Candidate implemented; independent reexamination pending. |

The protocol's abbreviated `NOT_ELIGIBLE` literal was also corrected to the checker wire value `NOT_ELIGIBLE_FOR_SCORED_EXAMINATION`.

## Verification obligations and claim boundary

- The repair author executed **50/50** repository tests (14 comparator + 36 participation, including five additional test methods) using both CPython **3.12.14** and **3.13.5**. Regressions cover direct-call/CLI high/low lone surrogates, nested text, valid supplementary characters and escaped pairs, ordinary/oversized numeric tokens, and duplicate keys. These are builder-side results and require independent reexamination.
- The original valid example declaration retains parsed-JSON digest `701326610d0fbbb592e952cf13435b006c42cbe59fe124d717189b7c390729f3`, as checked by a pinned-value test and an independent local replay. The **complete** report legitimately differs in `checker_version` from the predecessor.
- A newly executed local 7,200-cell matrix using five identity bases × four abilities × four evidence-access levels × two material-gap states × three ownership states × five decision statuses × three support states reproduced **2,880 abstentions / 4,311 ineligible / 9 pending**, with zero true authority booleans. This is a finite builder-side regression, not independent acceptance or complete input-space coverage.
- Preserve both adverse reviews and historical commits. No source-byte custody, provider authentication, independent decision-basis authentication, model qualification, or operational admission is asserted by this formal-screen repair.
- Earlier receipt-comparator findings remain unresolved and outside this PR.

**Disposition:** `SECOND_REPAIR_CANDIDATE / INDEPENDENT_REEXAMINATION_REQUIRED / SCORING_QUALIFICATION_NOT_ESTABLISHED / OPERATIONAL_ADMISSION_WITHHELD / PR_UNMERGED`.
