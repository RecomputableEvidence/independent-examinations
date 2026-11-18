"""Adversarial tests of the two model participation formal gates."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_model_participation import (  # noqa: E402
    ParticipationError, load_record, screen_participation, validate_participation,
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
