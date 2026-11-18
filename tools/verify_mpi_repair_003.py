#!/usr/bin/env python3
"""Finite predecessor/successor behavior comparison, not model qualification."""
import argparse
import copy
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--predecessor", required=True, type=Path,
                    help="Exact frozen MPI_SCREEN_0.1.2 source obtained separately")
args = parser.parse_args()
PREDECESSOR = args.predecessor
SUCCESSOR = ROOT / "tools" / "check_model_participation.py"
EXAMPLE = ROOT / "examples" / "model_participation_ready.json"

def frozen_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

assert frozen_blob(PREDECESSOR) == "382c92b7452b836cdcdb8154cf249bbf712a40a2"

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

old = load_module("frozen_mpi_012", PREDECESSOR)
new = load_module("repaired_mpi_013", SUCCESSOR)
seed = json.loads(EXAMPLE.read_text(encoding="utf-8"))
counts = Counter()
cases = 0
for basis, ability, access, gaps, ownership, status, support in itertools.product(
    ("PROVIDER_METADATA", "EXECUTOR_METADATA", "SYSTEM_DISCLOSED", "SELF_REPORTED", "UNKNOWN"),
    ("READY", "LIMITED", "UNABLE", "UNKNOWN"),
    ("SUFFICIENT", "PARTIAL", "INSUFFICIENT", "UNKNOWN"),
    (False, True),
    ("OWN_ASSESSMENT", "REPEATED_REFERENCE", "UNKNOWN"),
    ("CONTINUE", "WITHHOLD", "STOP", "UNRESOLVED", "ABSTAIN"),
    ("COMPLETE", "NO_LINKS", "NO_LIMITATIONS"),
):
    row = copy.deepcopy(seed)
    row["model_identity"]["basis"] = basis
    row["informedness"].update(
        ability=ability, evidence_access=access,
        material_gaps=["synthetic current grant gap"] if gaps else [],
    )
    dec = row["decision"]
    dec["ownership"] = ownership
    dec["status"] = status
    if support == "NO_LINKS":
        dec["decisive_links"] = []
    if support == "NO_LIMITATIONS":
        dec["counterevidence_or_limits"] = []
    a = old.screen_participation(row)
    b = new.screen_participation(row)
    assert a["checker_version"] == "MPI_SCREEN_0.1.2"
    assert b["checker_version"] == "MPI_SCREEN_0.1.3"
    a.pop("checker_version")
    b.pop("checker_version")
    assert a == b, (basis, ability, access, gaps, ownership, status, support)
    assert not any(b[k] for k in (
        "independent_model_identity_authenticated",
        "independent_decision_basis_authenticated",
        "qualified_for_scored_examination",
        "operational_admission",
    ))
    counts[b["disposition"]] += 1
    cases += 1

assert cases == 7200
assert new.screen_participation(copy.deepcopy(seed))["declaration_digest_sha256"] == (
    "701326610d0fbbb592e952cf13435b006c42cbe59fe124d717189b7c390729f3"
)
print(json.dumps({
    "scope": "finite_synthetic_declared_input_differential_not_model_truth",
    "python": platform.python_version(),
    "candidate_checker_sha256": hashlib.sha256(SUCCESSOR.read_bytes()).hexdigest(),
    "cases": cases, "equal_modulo_version": cases,
    "dispositions": dict(counts),
    "authority_true": 0,
}, indent=2, sort_keys=True))
