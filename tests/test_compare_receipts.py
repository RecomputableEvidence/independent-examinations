"""Standard-library tests of neutral comparison and strict evidence validation."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from compare_receipts import ReceiptError, compare, load_receipt, main, validate_receipt  # noqa: E402


def receipt():
    return {
        "schema_version": "0.1", "experiment_id": "SYNTHETIC-DEMO",
        "subject_sha256": "a" * 64, "implementation_id": "left",
        "platform_id": "demo-platform-left",
        "results": [
            {"case_id": "C01", "arm": "A", "cohort": "registered",
             "status": "CONTINUE", "reason": "MATCH", "exception": None}
        ],
    }


class ComparisonTests(unittest.TestCase):
    def test_exact_agreement_and_metadata(self):
        left = receipt()
        right = copy.deepcopy(left)
        right["implementation_id"] = "independent"
        result = compare(left, right)
        self.assertEqual(result["categories"], {"exact_agreement": 1})
        self.assertFalse(result["external_authority_verified"])
        self.assertFalse(result["operational_admission"])

    def test_right_more_permissive(self):
        left = receipt()
        left["results"][0]["status"] = "WITHHOLD"
        right = receipt()
        self.assertEqual(compare(left, right)["categories"], {"right_more_permissive": 1})

    def test_right_more_restrictive(self):
        left = receipt()
        right = receipt()
        right["results"][0].update(status="WITHHOLD", reason="NO_SCOPE")
        self.assertEqual(compare(left, right)["categories"], {"right_more_restrictive": 1})

    def test_reason_disagreement(self):
        left = receipt()
        right = receipt()
        right["results"][0]["reason"] = "DIFFERENT"
        self.assertEqual(compare(left, right)["categories"], {"reason_disagreement": 1})

    def test_exception_never_scored_as_withhold(self):
        left = receipt()
        right = receipt()
        right["results"][0].update(status="EXCEPTION", reason=None, exception="TypeError")
        self.assertEqual(compare(left, right)["categories"], {"exception_outcome": 1})

    def test_even_identical_exceptions_are_not_normal_agreement(self):
        left = receipt()
        left["results"][0].update(status="EXCEPTION", reason=None, exception="TypeError")
        self.assertEqual(compare(left, copy.deepcopy(left))["categories"], {"exception_outcome": 1})

    def test_missing_row(self):
        left = receipt()
        right = receipt()
        right["results"][0]["case_id"] = "C02"
        self.assertEqual(compare(left, right)["categories"], {"left_missing": 1, "right_missing": 1})

    def test_incomparable_subject_digest(self):
        left = receipt()
        right = receipt()
        right["subject_sha256"] = "b" * 64
        with self.assertRaises(ReceiptError):
            compare(left, right)

    def test_duplicate_case_arm(self):
        left = receipt()
        left["results"].append(copy.deepcopy(left["results"][0]))
        with self.assertRaises(ReceiptError):
            validate_receipt(left)

    def test_malformed_decisions_do_not_become_withhold(self):
        left = receipt()
        left["results"][0]["status"] = "EXCEPTION"
        with self.assertRaises(ReceiptError):
            validate_receipt(left)

    def test_schema_is_parseable_and_matches_contract(self):
        schema_path = Path(__file__).resolve().parents[1] / "schema" / "receipt-v0.1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(receipt()))
        self.assertEqual(schema["properties"]["schema_version"]["const"], "0.1")
        validate_receipt(receipt())

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(ReceiptError):
                load_receipt(path)

    def test_nan_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(ReceiptError):
                load_receipt(path)

    def test_cli_exit_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            left, right, output = (Path(tmp) / name for name in ("left.json", "right.json", "out.json"))
            l = receipt()
            r = receipt()
            r["results"][0]["reason"] = "DIFFERENT"
            left.write_text(json.dumps(l), encoding="utf-8")
            right.write_text(json.dumps(r), encoding="utf-8")
            self.assertEqual(main([str(left), str(right), "--output", str(output)]), 0)
            self.assertEqual(main([str(left), str(right), "--strict-equivalence", "--output", str(output)]), 1)
            self.assertEqual(json.loads(output.read_text())["categories"], {"reason_disagreement": 1})


if __name__ == "__main__":
    unittest.main()
