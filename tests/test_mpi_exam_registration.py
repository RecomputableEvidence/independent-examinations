"""Design-integrity checks, NOT an execution or qualification of any model."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "examinations" / "MPI-QUAL-001" / "CASE_REGISTRY.json"
SHA1 = re.compile(r"[0-9a-f]{40}\Z")


class MPIRegistrationTests(unittest.TestCase):
    def test_frozen_candidate_identity_and_provisional_disposition(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["registration_id"], "MPI-QUAL-001")
        self.assertEqual(data["registration_state"], "DESIGN_ONLY_NOT_RUN")
        self.assertTrue(SHA1.fullmatch(data["candidate_commit"]))
        self.assertTrue(SHA1.fullmatch(data["candidate_checker_blob"]))
        self.assertFalse(data["examiner_metadata_authenticated"])
        self.assertFalse(data["participating_models_authenticated"])
        self.assertFalse(data["case_truth_independently_established"])
        self.assertFalse(data["qualified_for_scored_examination"])
        self.assertFalse(data["operational_admission"])

    def test_all_twelve_registered_challenges_are_unique_and_bounded(self):
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cases = data["cases"]
        self.assertEqual(len(cases), 12)
        self.assertEqual({c["id"] for c in cases}, {f"I{i:02d}" for i in range(1, 7)} | {f"D{i:02d}" for i in range(1, 7)})
        self.assertTrue(all(set(c) == {"id", "family", "control", "challenge", "expected_gate"} for c in cases))
        self.assertEqual({c["family"] for c in cases}, {"identity", "decision"})
        self.assertTrue({"positive", "adverse", "withheld"} <= {c["control"] for c in cases})
        self.assertTrue(all(c["expected_gate"] in {"PENDING_INDEPENDENT_REVIEW", "RETAIN_NOT_SCORED", "NOT_QUALIFIED", "NOT_QUALIFIED_IF_CONTINUED"} for c in cases))


if __name__ == "__main__":
    unittest.main()
