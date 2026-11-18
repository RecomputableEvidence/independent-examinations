#!/usr/bin/env python3
"""Preflight local MPI-QUAL-001 evidence bytes; NEVER authenticate or qualify."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

REGISTRY = Path(__file__).resolve().parents[1] / "examinations/MPI-QUAL-001/CASE_REGISTRY.json"
PINNED_REGISTRY_SHA256 = "76ec97465c1aff6e7d8c789caab41cc0f22ec852f5ce526ae28a0d8613377025"
PINNED_CHECKER_SHA256 = "c8cbb0f9cfef3f222da70fa9fceb786d8b84a394cc63130e866aee35c7515635"
REGISTRATION_COMMIT = "537218d2b2434733bf934819e9ae0c2e563750c4"
CANDIDATE_COMMIT = "90b54ee3970d2e1e2520ee8b4b0ea3a6c36b383b"
MAX_MANIFEST_BYTES = 250_000
MAX_ARTIFACT_BYTES = 32_000_000
HEX = re.compile(r"[0-9a-f]{64}\Z")
MANIFEST_FIELDS = {
    "schema_version", "registration_id", "registration_commit",
    "registration_registry_sha256", "candidate_commit", "intake_state",
    "examiner", "artifacts", "model_runs", "claim_boundary",
}
EXAMINER_FIELDS = {"identity_claim", "platform_claim", "independence_disclosure"}
ARTIFACT_FIELDS = {
    "artifact_id", "role", "case_id", "relative_path", "sha256",
    "origin", "rights_status", "witness_ref",
}
RUN_FIELDS = {
    "run_id", "case_id", "model_id_claim", "provider_metadata_artifact_id",
    "model_input_artifact_id", "model_output_artifact_id", "declaration_artifact_id",
}
GLOBAL_ROLES = {"candidate_source", "examiner_harness", "rights_record"}
CASE_ROLES = {"governing_contract", "evidence_snapshot", "case_truth", "blinded_reference"}
RUN_ROLES = {"provider_run_metadata", "model_input", "model_output", "model_declaration"}
ROLES = GLOBAL_ROLES | CASE_ROLES | RUN_ROLES
ORIGINS = {"EXAMINER_OBTAINED", "PROVIDER_OBTAINED", "CANDIDATE_DECLARED", "UNKNOWN"}
RIGHTS = {"CLEARED", "RESTRICTED", "UNKNOWN"}
CLAIM_BOUNDARY = "LOCAL_BYTE_INVENTORY_ONLY_NO_AUTHENTICATION_NO_QUALIFICATION_NO_ADMISSION"


class IntakeError(ValueError):
    """Malformed evidence manifest, not an adverse model judgment."""


def exact_object(value, fields, label):
    if type(value) is not dict or set(value) != fields:
        raise IntakeError(f"{label} fields mismatch")


def scalar(value, label, *, limit=512):
    if (type(value) is not str or not value.strip() or len(value) > limit
            or any(0xD800 <= ord(c) <= 0xDFFF for c in value)):
        raise IntakeError(f"invalid {label}")
    return value


def fixed_sha(value, label):
    if type(value) is not str or not HEX.fullmatch(value):
        raise IntakeError(f"invalid {label}")


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def reject_number(value):
    raise IntakeError("manifest has no JSON numeric fields")


def reject_constant(value):
    raise IntakeError(f"invalid JSON constant {value}")


def bounded_regular_bytes(path, limit):
    path = Path(path)
    meta = path.stat()
    if not stat.S_ISREG(meta.st_mode):
        raise IntakeError("expected a regular file")
    if meta.st_size > limit:
        raise IntakeError(f"file exceeds {limit}-byte bound")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise IntakeError(f"file exceeds {limit}-byte bound")
    return data


def load_manifest(path):
    try:
        data = bounded_regular_bytes(path, MAX_MANIFEST_BYTES)
        return json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicate_keys,
                          parse_constant=reject_constant, parse_int=reject_number,
                          parse_float=reject_number)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise IntakeError(f"cannot parse manifest: {exc}") from exc


def relative_artifact_path(value):
    scalar(value, "relative artifact path", limit=512)
    if "\\" in value or "\x00" in value or ":" in value:
        raise IntakeError("unsafe artifact path")
    path = PurePosixPath(value)
    if (path.is_absolute() or not path.parts or any(p in {".", ".."} for p in value.split("/"))
            or str(path) != value):
        raise IntakeError("artifact path must be a normalized relative POSIX path")
    return path


def validate_manifest(data, registry):
    exact_object(data, MANIFEST_FIELDS, "intake")
    if type(data["schema_version"]) is not str or data["schema_version"] != "0.1":
        raise IntakeError("unsupported intake schema")
    if type(data["registration_id"]) is not str or data["registration_id"] != "MPI-QUAL-001":
        raise IntakeError("wrong examination")
    if type(data["registration_commit"]) is not str or data["registration_commit"] != REGISTRATION_COMMIT:
        raise IntakeError("registration commit mismatch")
    if type(data["candidate_commit"]) is not str or data["candidate_commit"] != CANDIDATE_COMMIT:
        raise IntakeError("candidate commit mismatch")
    if (type(data["registration_registry_sha256"]) is not str
            or data["registration_registry_sha256"] != PINNED_REGISTRY_SHA256):
        raise IntakeError("registry hash mismatch")
    if (type(data["intake_state"]) is not str
            or data["intake_state"] not in {"PREPARATION_ONLY_NOT_RUN", "POST_RUN_UNADJUDICATED"}):
        raise IntakeError("invalid intake state")
    if type(data["claim_boundary"]) is not str or data["claim_boundary"] != CLAIM_BOUNDARY:
        raise IntakeError("invalid claim boundary")
    exact_object(data["examiner"], EXAMINER_FIELDS, "examiner")
    for field in EXAMINER_FIELDS:
        scalar(data["examiner"][field], f"examiner.{field}")
    if type(data["artifacts"]) is not list or len(data["artifacts"]) > 1000:
        raise IntakeError("artifacts must be a bounded list")
    if type(data["model_runs"]) is not list or len(data["model_runs"]) > 1000:
        raise IntakeError("model_runs must be a bounded list")
    registered_ids = {row["id"] for row in registry["cases"]}
    artifact_ids = set()
    for item in data["artifacts"]:
        exact_object(item, ARTIFACT_FIELDS, "artifact")
        scalar(item["artifact_id"], "artifact_id", limit=128)
        if item["artifact_id"] in artifact_ids:
            raise IntakeError("duplicate artifact_id")
        artifact_ids.add(item["artifact_id"])
        if type(item["role"]) is not str or item["role"] not in ROLES:
            raise IntakeError("invalid artifact role")
        if item["role"] in GLOBAL_ROLES:
            if item["case_id"] is not None:
                raise IntakeError("global artifact must have null case_id")
        elif type(item["case_id"]) is not str or item["case_id"] not in registered_ids:
            raise IntakeError("case/run artifact must use a registered case_id")
        relative_artifact_path(item["relative_path"])
        fixed_sha(item["sha256"], "artifact sha256")
        if item["role"] == "candidate_source" and item["sha256"] != PINNED_CHECKER_SHA256:
            raise IntakeError("candidate_source digest differs from pinned checker source")
        if type(item["origin"]) is not str or item["origin"] not in ORIGINS:
            raise IntakeError("invalid acquisition-origin declaration")
        if type(item["rights_status"]) is not str or item["rights_status"] not in RIGHTS:
            raise IntakeError("invalid rights status")
        if item["witness_ref"] is not None:
            scalar(item["witness_ref"], "witness_ref")
    run_ids = set()
    for run in data["model_runs"]:
        exact_object(run, RUN_FIELDS, "model_run")
        scalar(run["run_id"], "run_id", limit=128)
        scalar(run["model_id_claim"], "model_id_claim", limit=256)
        if run["run_id"] in run_ids:
            raise IntakeError("duplicate run_id")
        run_ids.add(run["run_id"])
        if type(run["case_id"]) is not str or run["case_id"] not in registered_ids:
            raise IntakeError("run has unknown registered case_id")
        for field in RUN_FIELDS - {"run_id", "model_id_claim", "case_id"}:
            scalar(run[field], field, limit=128)
    if data["intake_state"] == "PREPARATION_ONLY_NOT_RUN" and data["model_runs"]:
        raise IntakeError("NOT_RUN intake cannot contain claimed model runs")
    return data


def _local_artifact_path(root, relative):
    candidate = root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise IntakeError("symbolic-link artifact paths are unsupported")
    if root not in candidate.resolve(strict=False).parents:
        raise IntakeError("artifact escapes evidence root")
    return candidate


def preflight(data, root, registry):
    validate_manifest(data, registry)
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise IntakeError("bundle root is not a directory")
    entries = []
    by_id = {}
    available_roles = set()
    for item in data["artifacts"]:
        entry = {"artifact_id": item["artifact_id"], "role": item["role"],
                 "case_id": item["case_id"], "rights_status": item["rights_status"],
                 "claimed_origin": item["origin"], "witness_declared": item["witness_ref"] is not None}
        try:
            path = _local_artifact_path(root, relative_artifact_path(item["relative_path"]))
            digest = hashlib.sha256(bounded_regular_bytes(path, MAX_ARTIFACT_BYTES)).hexdigest()
            entry["sha256_matches"] = digest == item["sha256"]
            entry["byte_status"] = "MATCH" if entry["sha256_matches"] else "DIGEST_MISMATCH"
        except (OSError, IntakeError) as exc:
            entry["sha256_matches"] = False
            entry["byte_status"] = "MISSING_OR_UNREADABLE"
            entry["local_error_type"] = type(exc).__name__
        if entry["sha256_matches"]:
            available_roles.add((item["role"], item["case_id"]))
        by_id[item["artifact_id"]] = item
        entries.append(entry)
    missing_global = sorted(role for role in GLOBAL_ROLES if (role, None) not in available_roles)
    missing_by_case = {}
    for case in registry["cases"]:
        missing = sorted(role for role in CASE_ROLES if (role, case["id"]) not in available_roles)
        if missing:
            missing_by_case[case["id"]] = missing
    run_issues = []
    for run in data["model_runs"]:
        for field, role in (
            ("provider_metadata_artifact_id", "provider_run_metadata"),
            ("model_input_artifact_id", "model_input"),
            ("model_output_artifact_id", "model_output"),
            ("declaration_artifact_id", "model_declaration"),
        ):
            item = by_id.get(run[field])
            if (item is None or item["role"] != role or item["case_id"] != run["case_id"]
                    or (role, run["case_id"]) not in available_roles):
                run_issues.append({"run_id": run["run_id"], "field": field, "problem": "missing_or_wrong_artifact"})
    if not data["model_runs"]:
        run_issues.append({"problem": "no_provider_witnessed_model_run_submitted"})
    claimed_models_per_case = {
        row["id"]: sorted({run["model_id_claim"] for run in data["model_runs"]
                           if run["case_id"] == row["id"]
                           and run["model_id_claim"].strip().casefold() != "unknown"})
        for row in registry["cases"]
    }
    comparison_claim_gaps = sorted(
        case_id for case_id, models in claimed_models_per_case.items() if len(models) < 2
    )
    byte_exceptions = sum(row["byte_status"] != "MATCH" for row in entries)
    incomplete = bool(missing_global or missing_by_case or run_issues
                      or comparison_claim_gaps or byte_exceptions)
    return {
        "registration_id": data["registration_id"],
        "registration_commit": data["registration_commit"],
        "candidate_commit": data["candidate_commit"],
        "intake_state": data["intake_state"],
        "preflight_disposition": ("INCOMPLETE_EVIDENCE_INTAKE" if incomplete
                                  else "BYTES_PRESENT_PENDING_INDEPENDENT_ADJUDICATION"),
        "artifact_inventory": entries,
        "missing_global_roles": missing_global,
        "missing_case_roles": missing_by_case,
        "run_binding_gaps": run_issues,
        "declared_model_ids": sorted({run["model_id_claim"] for run in data["model_runs"]}),
        "declared_models_by_case": claimed_models_per_case,
        "cases_with_fewer_than_two_distinct_claimed_models": comparison_claim_gaps,
        "invalid_or_missing_byte_records": byte_exceptions,
        "independent_model_identity_authenticated": False,
        "independent_case_truth_authenticated": False,
        "qualified_for_scored_examination": False,
        "operational_admission": False,
        "claim_ceiling": CLAIM_BOUNDARY,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--bundle-root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        registry_raw = REGISTRY.read_bytes()
        if hashlib.sha256(registry_raw).hexdigest() != PINNED_REGISTRY_SHA256:
            raise IntakeError("local case registry differs from pinned registration")
        registry = json.loads(registry_raw)
        report = preflight(load_manifest(args.manifest), args.bundle_root, registry)
    except (IntakeError, OSError, ValueError, RecursionError) as exc:
        print(f"INVALID_MPI_INTAKE: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["preflight_disposition"] == "INCOMPLETE_EVIDENCE_INTAKE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
