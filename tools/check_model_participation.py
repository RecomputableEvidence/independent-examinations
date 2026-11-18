#!/usr/bin/env python3
"""Screen two model-participation declarations without certifying truth.

MPI-01: model identity and task-specific informedness.
MPI-02: independently inspectable decision account and claimed ownership.

The result is NEVER an independent model-identity attestation, scoring
qualification, correctness oracle, or operational admission.
Python 3.10+ standard library only; no examined code is executed.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 250_000
MAX_JSON_DEPTH = 64
CHECKER_VERSION = "MPI_SCREEN_0.1.2"
DIGEST_PROFILE = "SORTED_SCHEMA_CONSTRAINED_JSON_UTF8_V1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TOP_KEYS = {"schema_version", "experiment_id", "subject_sha256", "case_id", "arm", "run_id", "model_identity", "informedness", "decision"}
IDENTITY_KEYS = {"provider", "model_id", "version", "basis", "evidence_ref"}
INFORMED_KEYS = {"task_scope", "ability", "evidence_access", "material_gaps", "basis"}
DECISION_KEYS = {"status", "ownership", "basis_summary", "governing_rule_refs", "evidence_refs", "decisive_links", "counterevidence_or_limits", "change_condition"}
LINK_KEYS = {"rule_ref", "evidence_ref", "why_material"}
IDENTITY_BASES = {"PROVIDER_METADATA", "EXECUTOR_METADATA", "SYSTEM_DISCLOSED", "SELF_REPORTED", "UNKNOWN"}
ABILITY = {"READY", "LIMITED", "UNABLE", "UNKNOWN"}
ACCESS = {"SUFFICIENT", "PARTIAL", "INSUFFICIENT", "UNKNOWN"}
DECISIONS = {"CONTINUE", "WITHHOLD", "STOP", "UNRESOLVED", "ABSTAIN"}
OWNERSHIP = {"OWN_ASSESSMENT", "REPEATED_REFERENCE", "UNKNOWN"}


class ParticipationError(ValueError):
    """Invalid format, not evidence that the model made a wrong decision."""


def nonempty(value, limit=512):
    """Require bounded nonblank Unicode scalar text for UTF-8 digest safety."""
    return (type(value) is str and bool(value.strip()) and len(value) <= limit
            and not any(0xD800 <= ord(char) <= 0xDFFF for char in value))


def canonical_identity_token(value):
    """Preserve case-sensitive actual IDs; reject surrounding whitespace."""
    return value is None or (type(value) is str and value == value.strip())


def is_unknown_identity(value):
    return value is None or (type(value) is str and value.casefold() == "unknown")


def declaration_digest_sha256(data):
    """Hash parsed, sorted JSON; NOT the original input bytes or a custody seal.

    This restricted record contains no JSON numbers, so float serialization
    cannot introduce cross-runtime representational ambiguity here.
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def exact_keys(value, keys, label):
    if type(value) is not dict or set(value) != keys:
        raise ParticipationError(f"{label} field mismatch")


def list_of_text(value, label):
    if type(value) is not list or len(value) > 100 or not all(nonempty(v, 256) for v in value):
        raise ParticipationError(f"{label} must be an array of nonempty strings")
    if len(set(value)) != len(value):
        raise ParticipationError(f"{label} contains duplicate references")


def validate_participation(data):
    """Always called from the public screen boundary, including direct calls."""
    exact_keys(data, TOP_KEYS, "participation")
    if data["schema_version"] != "0.1":
        raise ParticipationError("unsupported participation schema version")
    for key in ("experiment_id", "case_id", "arm", "run_id"):
        if not nonempty(data[key], 128):
            raise ParticipationError(f"invalid {key}")
    if type(data["subject_sha256"]) is not str or not SHA256.fullmatch(data["subject_sha256"]):
        raise ParticipationError("invalid subject_sha256")

    ident, informed, decision = (data[x] for x in ("model_identity", "informedness", "decision"))
    exact_keys(ident, IDENTITY_KEYS, "model_identity")
    exact_keys(informed, INFORMED_KEYS, "informedness")
    exact_keys(decision, DECISION_KEYS, "decision")
    if not nonempty(ident["provider"], 128):
        raise ParticipationError("invalid model provider")
    if not canonical_identity_token(ident["provider"]):
        raise ParticipationError("model provider has surrounding whitespace")
    for key in ("model_id", "version", "evidence_ref"):
        if ident[key] is not None and not nonempty(ident[key], 256):
            raise ParticipationError(f"invalid identity {key}")
    for key in ("model_id", "version"):
        if not canonical_identity_token(ident[key]):
            raise ParticipationError(f"identity {key} has surrounding whitespace")
    if type(ident["basis"]) is not str or ident["basis"] not in IDENTITY_BASES:
        raise ParticipationError("invalid identity basis")

    if not nonempty(informed["task_scope"]) or not nonempty(informed["basis"]):
        raise ParticipationError("informedness must specify task and basis")
    if type(informed["ability"]) is not str or informed["ability"] not in ABILITY:
        raise ParticipationError("invalid ability assessment")
    if type(informed["evidence_access"]) is not str or informed["evidence_access"] not in ACCESS:
        raise ParticipationError("invalid evidence access")
    list_of_text(informed["material_gaps"], "material_gaps")

    if type(decision["status"]) is not str or decision["status"] not in DECISIONS:
        raise ParticipationError("invalid decision status")
    if type(decision["ownership"]) is not str or decision["ownership"] not in OWNERSHIP:
        raise ParticipationError("invalid decision ownership declaration")
    for key in ("basis_summary", "change_condition"):
        if not nonempty(decision[key], 1024):
            raise ParticipationError(f"invalid {key}")
    for key in ("governing_rule_refs", "evidence_refs", "counterevidence_or_limits"):
        list_of_text(decision[key], key)
    links = decision["decisive_links"]
    if type(links) is not list or len(links) > 100:
        raise ParticipationError("decisive_links must be an array")
    for link in links:
        exact_keys(link, LINK_KEYS, "decisive_link")
        if not all(nonempty(link[key], 512) for key in LINK_KEYS):
            raise ParticipationError("invalid decisive link")
    return data


def screen_participation(data):
    """Formal checks only; never set qualification or authority true."""
    validate_participation(data)
    ident, informed, dec = (data[x] for x in ("model_identity", "informedness", "decision"))
    flags = {"MPI_01_identity": [], "MPI_01_informedness": [], "MPI_02_decision_path": []}

    if is_unknown_identity(ident["provider"]) or is_unknown_identity(ident["model_id"]):
        flags["MPI_01_identity"].append("MODEL_IDENTITY_NOT_DISCLOSED")
    if ident["basis"] in {"SELF_REPORTED", "UNKNOWN"}:
        flags["MPI_01_identity"].append("IDENTITY_UNVERIFIED_SELF_DECLARATION")
    if ident["basis"] in {"PROVIDER_METADATA", "EXECUTOR_METADATA", "SYSTEM_DISCLOSED"} and ident["evidence_ref"] is None:
        flags["MPI_01_identity"].append("IDENTITY_PROVENANCE_REFERENCE_MISSING")

    if informed["ability"] != "READY":
        flags["MPI_01_informedness"].append("INFORMED_CAPABILITY_NOT_ASSERTED")
    if informed["evidence_access"] != "SUFFICIENT":
        flags["MPI_01_informedness"].append("MATERIAL_EVIDENCE_ACCESS_NOT_ASSERTED")
    if informed["material_gaps"]:
        flags["MPI_01_informedness"].append("MATERIAL_GAPS_DISCLOSED")

    if dec["ownership"] != "OWN_ASSESSMENT":
        flags["MPI_02_decision_path"].append("OWN_DECISION_NOT_ASSERTED")
    if dec["status"] in {"CONTINUE", "WITHHOLD", "STOP"} and not dec["counterevidence_or_limits"]:
        flags["MPI_02_decision_path"].append("LIMITATIONS_ACCOUNT_MISSING")
    if not dec["governing_rule_refs"] or not dec["evidence_refs"] or not dec["decisive_links"]:
        flags["MPI_02_decision_path"].append("INDEPENDENTLY_INSPECTABLE_SUPPORT_MISSING")
    else:
        for link in dec["decisive_links"]:
            if link["rule_ref"] not in dec["governing_rule_refs"] or link["evidence_ref"] not in dec["evidence_refs"]:
                flags["MPI_02_decision_path"].append("DECISIVE_LINK_NOT_BOUND_TO_CITED_SUPPORT")
                break

    blocking = any(flags.values())
    if dec["status"] in {"ABSTAIN", "UNRESOLVED"}:
        disposition = "ABSTENTION_RETAINED_NOT_SCORED"
    elif blocking:
        disposition = "NOT_ELIGIBLE_FOR_SCORED_EXAMINATION"
    else:
        disposition = "FORMAL_SCREEN_PASS_PENDING_INDEPENDENT_REVIEW"

    return {
        "experiment_id": data["experiment_id"],
        "case_id": data["case_id"],
        "arm": data["arm"],
        "run_id": data["run_id"],
        "declared_model_id": ident["model_id"],
        "declared_model_provider": ident["provider"],
        "declared_decision_status": dec["status"],
        "identity_evidence_ref": ident["evidence_ref"],
        "subject_sha256": data["subject_sha256"],
        "schema_version": data["schema_version"],
        "checker_version": CHECKER_VERSION,
        "declaration_digest_sha256": declaration_digest_sha256(data),
        "declaration_digest_profile": DIGEST_PROFILE,
        "disposition": disposition,
        "invariant_flags": flags,
        "independent_model_identity_authenticated": False,
        "independent_decision_basis_authenticated": False,
        "qualified_for_scored_examination": False,
        "operational_admission": False,
        "claim_ceiling": "FORMAL_SELF_DECLARATION_SCREEN_ONLY",
    }


def _pairs_no_duplicates(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ParticipationError(f"duplicate JSON field: {k!r}")
        d[k] = v
    return d


def _reject_constant(value):
    raise ParticipationError(f"non-JSON numeric constant: {value}")


def _reject_number(value):
    """No numeric fields exist; reject tokens before integer/float conversion."""
    raise ParticipationError("JSON numbers are not valid participation fields")


def _check_json_depth(raw):
    """Check nesting before JSON decoding, ignoring brackets inside strings."""
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
                raise ParticipationError("JSON nesting depth exceeds limit")
        elif char in "}]":
            level -= 1
            if level < 0:
                raise ParticipationError("unbalanced JSON nesting")
    # The decoder handles unmatched open brackets and unterminated strings.


def load_record(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ParticipationError("declaration exceeds byte limit")
    try:
        raw = path.read_text(encoding="utf-8")
        _check_json_depth(raw)
        record = json.loads(raw,
                            object_pairs_hook=_pairs_no_duplicates,
                            parse_constant=_reject_constant,
                            parse_int=_reject_number,
                            parse_float=_reject_number)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ParticipationError(f"cannot load declaration: {exc}") from exc
    return validate_participation(record)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", help="Model's declaration (synthetic/demo or attributed)")
    args = parser.parse_args(argv)
    try:
        output = screen_participation(load_record(args.record))
    except (ParticipationError, OSError) as exc:
        print("INVALID_MODEL_PARTICIPATION_RECORD: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
