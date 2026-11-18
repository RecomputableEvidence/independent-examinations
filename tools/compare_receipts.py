#!/usr/bin/env python3
"""Compare independently supplied examination outputs; never adjudicate truth.

Python 3.10+ standard library. No imports or execution of examined implementations.
Invalid/malformed input is a validation error, not a candidate WITHHOLD.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

MAX_INPUT_BYTES = 8_000_000
MAX_JSON_DEPTH = 64
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
STATUSES = {"CONTINUE", "WITHHOLD", "STOP", "UNRESOLVED", "EXCEPTION"}
COHORTS = {"registered", "exploratory", "holdout_revealed"}
TOP_KEYS = {"schema_version", "experiment_id", "subject_sha256", "implementation_id", "platform_id", "results"}
ROW_KEYS = {"case_id", "arm", "cohort", "status", "reason", "exception"}


class ReceiptError(ValueError):
    """Invalid evidence representation; cannot compare safely."""


def nonempty(value, limit=128):
    return type(value) is str and 0 < len(value) <= limit


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReceiptError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_json_constant(value):
    raise ReceiptError(f"non-JSON number constant: {value}")


def reject_json_number(value):
    """No numeric fields exist in the receipt schema."""
    raise ReceiptError("JSON number not permitted in receipt")


def check_json_depth(raw):
    """Bound structural nesting before decoding, ignoring brackets in strings."""
    level = 0
    in_string = False
    escaped = False
    for char in raw:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "{[":
            level += 1
            if level > MAX_JSON_DEPTH:
                raise ReceiptError("JSON nesting depth exceeds limit")
        elif char in "}]":
            level -= 1
            if level < 0:
                raise ReceiptError("unbalanced JSON nesting")


def load_receipt(path):
    path = Path(path)
    try:
        # One bounded read from one open handle; no stat/read time-of-check gap.
        with path.open("rb") as source:
            raw_bytes = source.read(MAX_INPUT_BYTES + 1)
        if len(raw_bytes) > MAX_INPUT_BYTES:
            raise ReceiptError(f"receipt too large: {path}")
        raw = raw_bytes.decode("utf-8")
        check_json_depth(raw)
        obj = json.loads(raw,
                         object_pairs_hook=reject_duplicate_keys,
                         parse_constant=reject_json_constant,
                         parse_int=reject_json_number,
                         parse_float=reject_json_number)
    except ReceiptError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ReceiptError(f"cannot read valid JSON receipt {path}: {exc}") from exc
    validate_receipt(obj)
    return obj


def validate_receipt(obj):
    if type(obj) is not dict or set(obj) != TOP_KEYS:
        raise ReceiptError("receipt top-level field mismatch")
    if obj["schema_version"] != "0.1":
        raise ReceiptError("unsupported schema version")
    for key in ("experiment_id", "implementation_id", "platform_id"):
        if not nonempty(obj[key]):
            raise ReceiptError(f"invalid {key}")
    digest = obj["subject_sha256"]
    if type(digest) is not str or not SHA256.fullmatch(digest):
        raise ReceiptError("invalid subject_sha256")
    rows = obj["results"]
    if type(rows) is not list or not rows:
        raise ReceiptError("results must be a nonempty array")
    observed = set()
    for index, row in enumerate(rows):
        if type(row) is not dict or set(row) != ROW_KEYS:
            raise ReceiptError(f"result[{index}] field mismatch")
        if not nonempty(row["case_id"]) or not nonempty(row["arm"]):
            raise ReceiptError(f"result[{index}] invalid case_id or arm")
        if type(row["cohort"]) is not str or row["cohort"] not in COHORTS:
            raise ReceiptError(f"result[{index}] invalid cohort")
        status = row["status"]
        if type(status) is not str or status not in STATUSES:
            raise ReceiptError(f"result[{index}] invalid status")
        if status == "EXCEPTION":
            if row["reason"] is not None or not nonempty(row["exception"], 255):
                raise ReceiptError(f"result[{index}] invalid exception representation")
        elif not nonempty(row["reason"], 255) or row["exception"] is not None:
            raise ReceiptError(f"result[{index}] invalid decision representation")
        key = (row["case_id"], row["arm"])
        if key in observed:
            raise ReceiptError(f"duplicate case/arm observation: {key}")
        observed.add(key)


def comparison_dimensions(a, b):
    """Independent descriptive axes, with None for unavailable comparisons."""
    left_exception = None if a is None else a["status"] == "EXCEPTION"
    right_exception = None if b is None else b["status"] == "EXCEPTION"
    dims = {
        "cohort_equal": None,
        "status_equal": None,
        "reason_equal": None,
        "exception_equal": None,
        "left_has_exception": left_exception,
        "right_has_exception": right_exception,
        "continuation_relation": None,
    }
    if a is None or b is None:
        return dims
    dims["cohort_equal"] = a["cohort"] == b["cohort"]
    dims["status_equal"] = a["status"] == b["status"]
    if left_exception and right_exception:
        dims["exception_equal"] = a["exception"] == b["exception"]
    if not (left_exception or right_exception):
        dims["reason_equal"] = a["reason"] == b["reason"]
        lc, rc = a["status"] == "CONTINUE", b["status"] == "CONTINUE"
        dims["continuation_relation"] = (
            "BOTH_CONTINUE" if lc and rc else
            "LEFT_ONLY_CONTINUE" if lc else
            "RIGHT_ONLY_CONTINUE" if rc else
            "NEITHER_CONTINUE"
        )
    return dims


def compare(left, right):
    """Descriptive comparison; left and right have *no* oracle authority."""
    # Also validate direct library callers: dictionaries must not overwrite rows.
    validate_receipt(left)
    validate_receipt(right)
    for key in ("experiment_id", "subject_sha256"):
        if left[key] != right[key]:
            raise ReceiptError(f"incomparable {key}")
    lmap = {(r["case_id"], r["arm"]): r for r in left["results"]}
    rmap = {(r["case_id"], r["arm"]): r for r in right["results"]}
    counts = Counter()
    details = []
    per_key_dimensions = []
    dimension_totals = {key: Counter() for key in (
        "cohort_equal", "status_equal", "reason_equal", "exception_equal",
        "left_has_exception", "right_has_exception", "continuation_relation")}
    for case_id, arm in sorted(set(lmap) | set(rmap)):
        a = lmap.get((case_id, arm))
        b = rmap.get((case_id, arm))
        if a is None:
            kind = "left_missing"
        elif b is None:
            kind = "right_missing"
        elif a["cohort"] != b["cohort"]:
            kind = "cohort_disagreement"
        elif a["status"] == "EXCEPTION" or b["status"] == "EXCEPTION":
            kind = "exception_outcome"
        elif a["status"] == b["status"] and a["reason"] == b["reason"]:
            kind = "exact_agreement"
        elif a["status"] == b["status"]:
            kind = "reason_disagreement"
        elif b["status"] == "CONTINUE" and a["status"] != "CONTINUE":
            kind = "right_more_permissive"
        elif a["status"] == "CONTINUE" and b["status"] != "CONTINUE":
            kind = "right_more_restrictive"
        else:
            kind = "decision_disagreement"
        counts[kind] += 1
        dims = comparison_dimensions(a, b)
        per_key_dimensions.append({"case_id": case_id, "arm": arm,
                                   "primary_category": kind, **dims})
        for dimension, value in dims.items():
            bucket = ("not_applicable" if value is None else
                      "true" if value is True else
                      "false" if value is False else value)
            dimension_totals[dimension][bucket] += 1
        if kind != "exact_agreement":
            details.append({"case_id": case_id, "arm": arm, "category": kind,
                            "left": a, "right": b})
    return {
        "disposition": "DESCRIPTIVE_ONLY_NOT_AN_INDEPENDENT_TRUTH_ORACLE",
        "experiment_id": left["experiment_id"],
        "subject_sha256": left["subject_sha256"],
        "left_implementation": left["implementation_id"],
        "left_platform": left["platform_id"],
        "right_implementation": right["implementation_id"],
        "right_platform": right["platform_id"],
        "compared_keys": len(set(lmap) | set(rmap)),
        "categories": dict(sorted(counts.items())),
        "disagreements_and_exceptions": details,
        "per_key_dimensions": per_key_dimensions,
        "dimension_totals": {key: dict(sorted(totals.items()))
                             for key, totals in sorted(dimension_totals.items())},
        "external_authority_verified": False,
        "operational_admission": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", help="First receipt; not an oracle")
    parser.add_argument("right", help="Second receipt; not an oracle")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--strict-equivalence", action="store_true",
                        help="Exit 1 on any disagreement or exception (default: report neutrally)")
    args = parser.parse_args(argv)
    try:
        result = compare(load_receipt(args.left), load_receipt(args.right))
        out = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
        else:
            sys.stdout.write(out)
        if args.strict_equivalence and result["disagreements_and_exceptions"]:
            return 1
        return 0
    except (ReceiptError, OSError) as exc:
        print(f"RECEIPT_VALIDATION_ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
