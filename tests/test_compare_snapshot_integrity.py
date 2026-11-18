"""Registered report-snapshot mutation regressions; no custody claim."""

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compare_receipts import compare  # noqa: E402


def receipt(status, reason="COMMON", case_id="C01", exception=None):
    return {
        "schema_version": "0.1", "experiment_id": "SNAPSHOT-SYNTHETIC",
        "subject_sha256": "a" * 64, "implementation_id": status,
        "platform_id": "synthetic-platform",
        "results": [{"case_id": case_id, "arm": "D", "cohort": "registered",
                     "status": status,
                     "reason": None if status == "EXCEPTION" else reason,
                     "exception": exception if status == "EXCEPTION" else None}],
    }


class SnapshotIntegrityTests(unittest.TestCase):
    def test_left_reason_mutation_cannot_rewrite_report(self):
        left, right = receipt("CONTINUE"), receipt("STOP")
        report = compare(left, right)
        frozen = json.dumps(report, sort_keys=True)
        self.assertTrue(report["per_key_dimensions"][0]["reason_equal"])
        left["results"][0]["reason"] = "CHANGED_AFTER_COMPARISON"
        self.assertEqual(report["disagreements_and_exceptions"][0]["left"]["reason"], "COMMON")
        self.assertEqual(json.dumps(report, sort_keys=True), frozen)

    def test_both_caller_rows_can_change_without_affecting_report(self):
        left, right = receipt("CONTINUE"), receipt("STOP")
        report = compare(left, right)
        frozen = copy.deepcopy(report)
        left["results"][0].update(status="WITHHOLD", reason="new", cohort="exploratory")
        right["results"][0].update(status="CONTINUE", reason="other", cohort="holdout_revealed")
        self.assertEqual(report, frozen)
        self.assertEqual(report["categories"], {"right_more_restrictive": 1})
        self.assertTrue(report["per_key_dimensions"][0]["reason_equal"])

    def test_exception_text_snapshot_preserves_computed_equality(self):
        left = receipt("EXCEPTION", exception="same exception")
        right = receipt("EXCEPTION", exception="same exception")
        report = compare(left, right)
        self.assertTrue(report["per_key_dimensions"][0]["exception_equal"])
        left["results"][0]["exception"] = "new exception"
        right["results"][0]["exception"] = "different exception"
        self.assertEqual(report["disagreements_and_exceptions"][0]["left"]["exception"], "same exception")
        self.assertEqual(report["disagreements_and_exceptions"][0]["right"]["exception"], "same exception")
        self.assertTrue(report["per_key_dimensions"][0]["exception_equal"])

    def test_new_comparison_reflects_new_input_while_old_remains_frozen(self):
        left, right = receipt("CONTINUE"), receipt("STOP")
        old = compare(left, right)
        left["results"][0].update(status="STOP", reason="revised")
        new = compare(left, right)
        self.assertEqual(old["categories"], {"right_more_restrictive": 1})
        self.assertEqual(old["disagreements_and_exceptions"][0]["left"]["status"], "CONTINUE")
        self.assertEqual(new["categories"], {"reason_disagreement": 1})
        self.assertEqual(new["disagreements_and_exceptions"][0]["left"]["reason"], "revised")
        self.assertFalse(new["per_key_dimensions"][0]["reason_equal"])

    def test_missing_row_snapshot_does_not_alias_present_side(self):
        left, right = receipt("CONTINUE", case_id="C01"), receipt("STOP", case_id="C02")
        report = compare(left, right)
        frozen = json.dumps(report, sort_keys=True)
        left["results"][0]["reason"] = "edited left"
        right["results"][0]["reason"] = "edited right"
        self.assertEqual(json.dumps(report, sort_keys=True), frozen)
        self.assertEqual(report["categories"], {"left_missing": 1, "right_missing": 1})

    def test_row_snapshot_is_distinct_from_both_input_row_containers(self):
        left, right = receipt("CONTINUE"), receipt("STOP")
        report = compare(left, right)
        detail = report["disagreements_and_exceptions"][0]
        self.assertIsNot(detail["left"], left["results"][0])
        self.assertIsNot(detail["right"], right["results"][0])


if __name__ == "__main__":
    unittest.main()
