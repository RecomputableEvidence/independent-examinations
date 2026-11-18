"""Registered comparator successor controls; descriptive, never a truth oracle."""

from collections import Counter
import copy
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compare_receipts import (  # noqa: E402
    MAX_INPUT_BYTES, ReceiptError, compare, load_receipt, main, validate_receipt,
)


def receipt(status="CONTINUE", cohort="registered", reason="same", exception=None):
    return {
        "schema_version": "0.1", "experiment_id": "REGISTERED-SYNTHETIC",
        "subject_sha256": "a" * 64, "implementation_id": "synthetic-left",
        "platform_id": "synthetic-platform-left",
        "results": [{"case_id": "C01", "arm": "D", "cohort": cohort,
                     "status": status,
                     "reason": None if status == "EXCEPTION" else reason,
                     "exception": exception if status == "EXCEPTION" else None}],
    }


def pair(a, b):
    b["implementation_id"] = "synthetic-right"
    b["platform_id"] = "synthetic-platform-right"
    validate_receipt(a)
    validate_receipt(b)
    return compare(a, b)


class ComparatorDimensionsTests(unittest.TestCase):
    def test_historical_six_case_categories_unchanged(self):
        left = load_receipt(ROOT / "examples" / "left.json")
        right = load_receipt(ROOT / "examples" / "right.json")
        output = compare(left, right)
        self.assertEqual(output["categories"], {
            "exact_agreement": 2, "right_more_permissive": 1,
            "right_more_restrictive": 1, "reason_disagreement": 1,
            "exception_outcome": 1,
        })
        self.assertEqual(len(output["per_key_dimensions"]), 6)
        self.assertFalse(output["external_authority_verified"])
        self.assertFalse(output["operational_admission"])

    def test_registered_225_branch_cross_product_unchanged(self):
        counts = Counter()
        for ls, rs, lc, rc in itertools.product(
            ("CONTINUE", "WITHHOLD", "STOP", "UNRESOLVED", "EXCEPTION"),
            ("CONTINUE", "WITHHOLD", "STOP", "UNRESOLVED", "EXCEPTION"),
            ("registered", "exploratory", "holdout_revealed"),
            ("registered", "exploratory", "holdout_revealed"),
        ):
            output = pair(receipt(ls, lc, exception="synthetic"),
                          receipt(rs, rc, exception="synthetic"))
            primary = next(iter(output["categories"]))
            counts[primary] += 1
            self.assertEqual(output["per_key_dimensions"][0]["primary_category"], primary)
            self.assertTrue(all(sum(t.values()) == 1 for t in output["dimension_totals"].values()))
        self.assertEqual(counts, {
            "cohort_disagreement": 150, "exception_outcome": 27,
            "decision_disagreement": 18, "exact_agreement": 12,
            "right_more_permissive": 9, "right_more_restrictive": 9,
        })

    def test_unchanged_exact_agreement_still_has_orthogonal_observation(self):
        output = pair(receipt(), receipt())
        self.assertEqual(output["categories"], {"exact_agreement": 1})
        self.assertEqual(output["disagreements_and_exceptions"], [])
        dims = output["per_key_dimensions"][0]
        self.assertTrue(dims["cohort_equal"])
        self.assertTrue(dims["status_equal"])
        self.assertTrue(dims["reason_equal"])
        self.assertIsNone(dims["exception_equal"])
        self.assertFalse(dims["left_has_exception"])
        self.assertFalse(dims["right_has_exception"])
        self.assertEqual(dims["continuation_relation"], "BOTH_CONTINUE")

    def test_identical_exception_kept_and_strict_cli_rejects(self):
        left = receipt("EXCEPTION", exception="TypeError")
        right = copy.deepcopy(left)
        output = pair(left, right)
        self.assertEqual(output["categories"], {"exception_outcome": 1})
        dims = output["per_key_dimensions"][0]
        self.assertTrue(dims["exception_equal"])
        self.assertTrue(dims["status_equal"])
        self.assertIsNone(dims["reason_equal"])
        with tempfile.TemporaryDirectory() as tmp:
            left_path, right_path, out_path = (Path(tmp) / name for name in ("left.json", "right.json", "out.json"))
            left_path.write_text(json.dumps(left), encoding="utf-8")
            right_path.write_text(json.dumps(right), encoding="utf-8")
            self.assertEqual(main([str(left_path), str(right_path), "--output", str(out_path)]), 0)
            self.assertEqual(main([str(left_path), str(right_path), "--strict-equivalence", "--output", str(out_path)]), 1)

    def test_different_exceptions_have_distinct_equality_flag(self):
        output = pair(receipt("EXCEPTION", exception="TypeError"),
                      receipt("EXCEPTION", exception="TimeoutError"))
        self.assertEqual(output["categories"], {"exception_outcome": 1})
        self.assertFalse(output["per_key_dimensions"][0]["exception_equal"])

    def test_cohort_mismatch_does_not_hide_exception_and_status(self):
        output = pair(receipt("EXCEPTION", "registered", exception="TypeError"),
                      receipt("WITHHOLD", "exploratory"))
        self.assertEqual(output["categories"], {"cohort_disagreement": 1})
        dims = output["per_key_dimensions"][0]
        self.assertFalse(dims["cohort_equal"])
        self.assertFalse(dims["status_equal"])
        self.assertTrue(dims["left_has_exception"])
        self.assertFalse(dims["right_has_exception"])
        self.assertIsNone(dims["reason_equal"])
        self.assertEqual(output["dimension_totals"]["status_equal"]["false"], 1)

    def test_continuation_relation_is_narrow_not_general_safety_order(self):
        for ls, rs, expected in (
            ("STOP", "CONTINUE", "RIGHT_ONLY_CONTINUE"),
            ("CONTINUE", "WITHHOLD", "LEFT_ONLY_CONTINUE"),
            ("WITHHOLD", "UNRESOLVED", "NEITHER_CONTINUE"),
        ):
            with self.subTest(ls=ls, rs=rs):
                output = pair(receipt(ls), receipt(rs))
                self.assertEqual(output["per_key_dimensions"][0]["continuation_relation"], expected)

    def test_missing_row_has_not_applicable_comparison_dimensions(self):
        left = receipt()
        right = receipt()
        right["results"][0]["case_id"] = "C02"
        output = pair(left, right)
        self.assertEqual(output["categories"], {"left_missing": 1, "right_missing": 1})
        for dims in output["per_key_dimensions"]:
            self.assertIsNone(dims["status_equal"])
            self.assertIsNone(dims["cohort_equal"])
            self.assertIsNone(dims["continuation_relation"])
        self.assertEqual(output["dimension_totals"]["status_equal"], {"not_applicable": 2})

    def test_direct_compare_rejects_duplicate_case_arm_without_overwrite(self):
        left = receipt()
        left["results"].append(copy.deepcopy(left["results"][0]))
        left["results"][1]["reason"] = "different"
        with self.assertRaises(ReceiptError):
            compare(left, receipt())

    def test_direct_compare_rejects_invalid_receipt_structure(self):
        left = receipt()
        left["results"][0]["status"] = "FORGED"
        with self.assertRaises(ReceiptError):
            compare(left, receipt())

    def test_one_bounded_read_rejects_oversized_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oversize.json"
            path.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
            with self.assertRaisesRegex(ReceiptError, "receipt too large"):
                load_receipt(path)

    def test_deep_json_rejected_with_controlled_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested.json"
            path.write_text("[" * 50_000 + "0" + "]" * 50_000, encoding="utf-8")
            with self.assertRaisesRegex(ReceiptError, "nesting depth"):
                load_receipt(path)

    def test_numeric_tokens_rejected_before_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "number.json"
            for token in ("0", "1.5", "8" * 5000):
                with self.subTest(token=token[:10]):
                    path.write_text('{"field":' + token + '}', encoding="utf-8")
                    with self.assertRaisesRegex(ReceiptError, "JSON number not permitted"):
                        load_receipt(path)

    def test_incomparable_subjects_still_rejected(self):
        left = receipt()
        right = receipt()
        right["subject_sha256"] = "b" * 64
        with self.assertRaisesRegex(ReceiptError, "incomparable subject_sha256"):
            compare(left, right)


if __name__ == "__main__":
    unittest.main()
