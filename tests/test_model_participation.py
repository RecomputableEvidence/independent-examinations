"""Adversarial tests of the two model participation formal gates."""

import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_model_participation import (  # noqa: E402
    ParticipationError, declaration_digest_sha256, load_record, main,
    screen_participation, validate_participation,
)


def example():
    return json.loads((ROOT / "examples" / "model_participation_ready.json").read_text(encoding="utf-8"))


class ParticipationTests(unittest.TestCase):
    def test_complete_declaration_reaches_review_not_qualification(self):
        result = screen_participation(example())
        self.assertEqual(result["disposition"], "FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW")
        self.assertFalse(result["qualified_for_scored_examination"])
        self.assertFalse(result["independent_model_identity_authenticated"])
        self.assertFalse(result["independent_decision_basis_authenticated"])
        self.assertFalse(result["operational_admission"])
        self.assertEqual(result["subject_sha256"], example()["subject_sha256"])
        self.assertEqual(result["declared_decision_status"], "WITHHOLD")
        self.assertEqual(result["identity_evidence_ref"], example()["model_identity"]["evidence_ref"])
        self.assertEqual(result["schema_version"], "0.1")
        self.assertEqual(result["checker_version"], "MPI_SCREEN_0.1.1")
        self.assertEqual(result["declaration_digest_sha256"], declaration_digest_sha256(example()))

    def test_continuation_eligible_only_for_further_review(self):
        rec = example()
        rec["decision"]["status"] = "CONTINUE"
        self.assertEqual(screen_participation(rec)["disposition"], "FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW")

    def test_self_reported_identity_is_not_verified(self):
        rec = example()
        rec["model_identity"]["basis"] = "SELF_REPORTED"
        result = screen_participation(rec)
        self.assertEqual(result["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")
        self.assertIn("IDENTITY_UNVERIFIED_SELF_DECLARATION", result["invariant_flags"]["MPI_01_identity"])

    def test_unknown_identity_fails_scored_gate(self):
        rec = example()
        rec["model_identity"].update(model_id=None, basis="UNKNOWN", evidence_ref=None)
        self.assertEqual(screen_participation(rec)["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")

    def test_unknown_provider_padded_is_rejected(self):
        rec = example()
        rec["model_identity"]["provider"] = " UNKNOWN "
        with self.assertRaises(ParticipationError):
            screen_participation(rec)

    def test_unknown_model_padded_is_rejected(self):
        rec = example()
        rec["model_identity"]["model_id"] = " UNKNOWN "
        with self.assertRaises(ParticipationError):
            screen_participation(rec)

    def test_unknown_case_variants_are_not_eligible(self):
        for key in ("provider", "model_id"):
            for sentinel in ("unknown", "Unknown", "UNKNOWN"):
                with self.subTest(key=key, sentinel=sentinel):
                    rec = example()
                    rec["model_identity"][key] = sentinel
                    self.assertEqual(screen_participation(rec)["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")

    def test_real_identifiers_remain_case_sensitive(self):
        left = example()
        right = copy.deepcopy(left)
        right["model_identity"]["model_id"] = left["model_identity"]["model_id"].upper()
        self.assertNotEqual(screen_participation(left)["declared_model_id"], screen_participation(right)["declared_model_id"])
        self.assertNotEqual(declaration_digest_sha256(left), declaration_digest_sha256(right))

    def test_metadata_without_provenance_reference_fails(self):
        rec = example()
        rec["model_identity"]["evidence_ref"] = None
        self.assertIn("IDENTITY_PROVENANCE_REFERENCE_MISSING", screen_participation(rec)["invariant_flags"]["MPI_01_identity"])

    def test_missing_evidence_access_fails(self):
        rec = example()
        rec["informedness"]["evidence_access"] = "PARTIAL"
        self.assertEqual(screen_participation(rec)["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")

    def test_limited_competence_fails(self):
        rec = example()
        rec["informedness"]["ability"] = "LIMITED"
        self.assertEqual(screen_participation(rec)["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")

    def test_material_gaps_fails_even_with_ready_claim(self):
        rec = example()
        rec["informedness"]["material_gaps"] = ["issuer source not provided"]
        self.assertIn("MATERIAL_GAPS_DISCLOSED", screen_participation(rec)["invariant_flags"]["MPI_01_informedness"])

    def test_repeating_expected_answer_fails(self):
        rec = example()
        rec["decision"]["ownership"] = "REPEATED_REFERENCE"
        self.assertEqual(screen_participation(rec)["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")

    def test_no_support_path_fails(self):
        rec = example()
        rec["decision"]["governing_rule_refs"] = []
        rec["decision"]["decisive_links"] = []
        self.assertIn("INDEPENDENTLY_INSPECTABLE_SUPPORT_MISSING", screen_participation(rec)["invariant_flags"]["MPI_02_decision_path"])

    def test_definitive_decision_requires_limit_account(self):
        for status in ("CONTINUE", "WITHHOLD", "STOP"):
            with self.subTest(status=status):
                rec = example()
                rec["decision"].update(status=status, counterevidence_or_limits=[])
                output = screen_participation(rec)
                self.assertEqual(output["disposition"], "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION")
                self.assertIn("LIMITATIONS_ACCOUNT_MISSING", output["invariant_flags"]["MPI_02_decision_path"])

    def test_explicit_no_known_limits_statement_is_formally_sufficient(self):
        rec = example()
        rec["decision"]["counterevidence_or_limits"] = ["No additional limits identified within stated synthetic case scope"]
        result = screen_participation(rec)
        self.assertEqual(result["disposition"], "FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW")
        self.assertFalse(result["independent_decision_basis_authenticated"])

    def test_unbound_support_link_fails(self):
        rec = example()
        rec["decision"]["decisive_links"][0]["evidence_ref"] = "uncited-evidence"
        self.assertIn("DECISIVE_LINK_NOT_BOUND_TO_CITED_SUPPORT", screen_participation(rec)["invariant_flags"]["MPI_02_decision_path"])

    def test_honest_abstention_retained_and_unscored(self):
        rec = example()
        rec["informedness"].update(ability="UNABLE", evidence_access="INSUFFICIENT", material_gaps=["missing source"])
        rec["decision"].update(status="ABSTAIN", ownership="OWN_ASSESSMENT", governing_rule_refs=[], evidence_refs=[], decisive_links=[], basis_summary="I cannot examine the current grant", change_condition="Provide authenticated grant evidence")
        result = screen_participation(rec)
        self.assertEqual(result["disposition"], "ABSTENTION_RETAINED_NOT_SCORED")
        self.assertFalse(result["qualified_for_scored_examination"])

    def test_abstention_does_not_need_invented_limitations(self):
        rec = example()
        rec["decision"].update(status="ABSTAIN", counterevidence_or_limits=[])
        self.assertEqual(screen_participation(rec)["disposition"], "ABSTENTION_RETAINED_NOT_SCORED")

    def test_unknown_model_abstention_retained(self):
        rec = example()
        rec["model_identity"].update(provider="UNKNOWN", model_id=None, basis="UNKNOWN", evidence_ref=None)
        rec["decision"]["status"] = "UNRESOLVED"
        self.assertEqual(screen_participation(rec)["disposition"], "ABSTENTION_RETAINED_NOT_SCORED")

    def test_malformed_decision_rejected_at_public_boundary(self):
        rec = example()
        del rec["decision"]["change_condition"]
        with self.assertRaises(ParticipationError):
            screen_participation(rec)

    def test_duplicate_references_rejected(self):
        rec = example()
        rec["decision"]["evidence_refs"] *= 2
        with self.assertRaises(ParticipationError):
            validate_participation(rec)

    def test_private_reasoning_trace_not_required(self):
        rec = example()
        self.assertNotIn("chain_of_thought", rec["decision"])
        self.assertNotIn("hidden_reasoning", rec["decision"])
        self.assertEqual(screen_participation(rec)["disposition"], "FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW")

    def test_material_substitutions_change_bound_report(self):
        baseline = screen_participation(example())
        changes = [
            ("subject_sha256", "", "b" * 64),
            ("status", "decision", "CONTINUE"),
            ("evidence_ref", "model_identity", "synthetic:other-metadata"),
        ]
        for key, section, value in changes:
            with self.subTest(key=key):
                rec = example()
                (rec if not section else rec[section])[key] = value
                result = screen_participation(rec)
                self.assertNotEqual(result, baseline)
                self.assertNotEqual(result["declaration_digest_sha256"], baseline["declaration_digest_sha256"])

    def test_sorted_parsed_json_digest_differs_from_raw_byte_hash(self):
        rec = example()
        first = json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        second = json.dumps(rec, indent=2, ensure_ascii=False)
        self.assertNotEqual(first, second)
        self.assertEqual(declaration_digest_sha256(json.loads(first)), declaration_digest_sha256(json.loads(second)))

    def test_json_brackets_inside_strings_do_not_count_as_nesting(self):
        rec = example()
        rec["decision"]["basis_summary"] = "[" * 500
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            path.write_text(json.dumps(rec), encoding="utf-8")
            self.assertEqual(load_record(path)["decision"]["basis_summary"], rec["decision"]["basis_summary"])

    def test_deep_json_is_controlled_invalid_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deep.json"
            path.write_text("[" * 50000 + "0" + "]" * 50000, encoding="utf-8")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                exit_code = main([str(path)])
            self.assertEqual(exit_code, 2)
            self.assertIn("nesting depth exceeds limit", err.getvalue())
            self.assertNotIn("Traceback", err.getvalue())

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            path.write_text('{"same":1,"same":2}', encoding="utf-8")
            with self.assertRaises(ParticipationError):
                load_record(path)

    def test_nan_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            path.write_text('{"x":NaN}', encoding="utf-8")
            with self.assertRaises(ParticipationError):
                load_record(path)

    def test_version_invalid(self):
        rec = example()
        rec["schema_version"] = "0.2"
        with self.assertRaises(ParticipationError):
            validate_participation(rec)

    def test_copy_does_not_change_original(self):
        base = example()
        modified = copy.deepcopy(base)
        modified["decision"]["status"] = "ABSTAIN"
        self.assertEqual(base["decision"]["status"], "WITHHOLD")


if __name__ == "__main__":
    unittest.main()
