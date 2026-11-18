"""Preflight input/adverse tests. These do NOT qualify a model or case truth."""

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_mpi_intake import (  # noqa: E402
    IntakeError, REGISTRY, load_manifest, preflight, validate_manifest,
)

TEMPLATE = ROOT / "examinations/MPI-QUAL-001/INTAKE_MANIFEST_TEMPLATE.json"


def manifest():
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def artifact(path, *, role="evidence_snapshot", case_id="I01", artifact_id="E01",
             sha256=None, origin="UNKNOWN", rights="UNKNOWN", witness=None):
    return {
        "artifact_id": artifact_id, "role": role, "case_id": case_id,
        "relative_path": path,
        "sha256": sha256 or "a" * 64,
        "origin": origin, "rights_status": rights, "witness_ref": witness,
    }


class MPIIntakeTests(unittest.TestCase):
    def test_empty_template_blocks_without_implying_negative_model_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = preflight(manifest(), tmp, registry())
        self.assertEqual(out["preflight_disposition"], "INCOMPLETE_EVIDENCE_INTAKE")
        self.assertEqual(len(out["missing_case_roles"]), 12)
        self.assertEqual(len(out["missing_global_roles"]), 3)
        self.assertEqual(len(out["cases_with_fewer_than_two_distinct_claimed_models"]), 12)
        self.assertEqual(out["run_binding_gaps"], [{"problem": "no_provider_witnessed_model_run_submitted"}])
        for key in ("independent_model_identity_authenticated",
                    "independent_case_truth_authenticated",
                    "qualified_for_scored_examination", "operational_admission"):
            self.assertIs(out[key], False)

    def test_template_cli_is_controlled_incomplete_not_qualification(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/verify_mpi_intake.py"),
                 str(TEMPLATE), "--bundle-root", tmp],
                capture_output=True, text=True, timeout=5,
            )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["preflight_disposition"], "INCOMPLETE_EVIDENCE_INTAKE")
        self.assertNotIn("Traceback", result.stderr)

    def test_corrupted_registry_coordinate_cannot_be_silently_accepted(self):
        rec = manifest()
        rec["registration_registry_sha256"] = "b" * 64
        with self.assertRaisesRegex(IntakeError, "registry hash"):
            validate_manifest(rec, registry())

    def test_adversarial_custom_state_object_is_controlled_error(self):
        class StateImpostor:
            def __eq__(self, value):
                return value == "PREPARATION_ONLY_NOT_RUN"

        rec = manifest()
        rec["intake_state"] = StateImpostor()
        with self.assertRaisesRegex(IntakeError, "intake state"):
            validate_manifest(rec, registry())

    def test_wrong_pinned_candidate_source_hash_rejected(self):
        rec = manifest()
        rec["artifacts"] = [artifact(
            "checker.py", role="candidate_source", case_id=None,
            artifact_id="CANDIDATE", sha256="0" * 64,
        )]
        with self.assertRaisesRegex(IntakeError, "pinned checker"):
            validate_manifest(rec, registry())

    def test_relative_path_traversal_and_absolute_paths_rejected(self):
        for path in ("../escape.json", "/etc/passwd", "a//b.json", "a/./b.json", "C:\\secret.json"):
            with self.subTest(path=path):
                rec = manifest()
                rec["artifacts"] = [artifact(path)]
                with self.assertRaises(IntakeError):
                    validate_manifest(rec, registry())

    def test_duplicate_artifact_ids_rejected(self):
        rec = manifest()
        rec["artifacts"] = [artifact("one.json"), artifact("two.json")]
        with self.assertRaisesRegex(IntakeError, "duplicate artifact_id"):
            validate_manifest(rec, registry())

    def test_wrong_case_role_binding_rejected(self):
        rec = manifest()
        rec["artifacts"] = [artifact("evidence.json", role="case_truth", case_id=None)]
        with self.assertRaisesRegex(IntakeError, "registered case_id"):
            validate_manifest(rec, registry())

    def test_matched_bytes_are_inventory_not_authentication(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = b"synthetic untrusted evidence for intake only"
            (Path(tmp) / "evidence.txt").write_bytes(data)
            rec = manifest()
            rec["artifacts"] = [artifact(
                "evidence.txt", sha256=hashlib.sha256(data).hexdigest(),
                origin="PROVIDER_OBTAINED", rights="CLEARED",
                witness="synthetic:claimed-witness-not-verified",
            )]
            out = preflight(rec, tmp, registry())
        self.assertEqual(out["artifact_inventory"][0]["byte_status"], "MATCH")
        self.assertEqual(out["preflight_disposition"], "INCOMPLETE_EVIDENCE_INTAKE")
        self.assertIs(out["independent_model_identity_authenticated"], False)
        self.assertIs(out["independent_case_truth_authenticated"], False)

    def test_digest_mismatch_preserved_as_explicit_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "evidence.txt").write_bytes(b"wrong bytes")
            rec = manifest()
            rec["artifacts"] = [artifact("evidence.txt", sha256=hashlib.sha256(b"expected").hexdigest())]
            out = preflight(rec, tmp, registry())
        self.assertEqual(out["artifact_inventory"][0]["byte_status"], "DIGEST_MISMATCH")
        self.assertEqual(out["invalid_or_missing_byte_records"], 1)

    def test_declared_run_without_artifact_links_retained_as_gap(self):
        rec = manifest()
        rec["intake_state"] = "POST_RUN_UNADJUDICATED"
        rec["model_runs"] = [{
            "run_id": "synthetic-run", "case_id": "D01", "model_id_claim": "UNKNOWN",
            "provider_metadata_artifact_id": "missing-metadata",
            "model_input_artifact_id": "missing-input",
            "model_output_artifact_id": "missing-output",
            "declaration_artifact_id": "missing-declaration",
        }]
        with tempfile.TemporaryDirectory() as tmp:
            out = preflight(rec, tmp, registry())
        self.assertEqual(len(out["run_binding_gaps"]), 4)
        self.assertEqual(out["declared_model_ids"], ["UNKNOWN"])
        self.assertIs(out["qualified_for_scored_examination"], False)

    def test_not_run_manifest_cannot_contain_model_runs(self):
        rec = manifest()
        rec["model_runs"] = [{
            "run_id": "synthetic-run", "case_id": "D01", "model_id_claim": "UNKNOWN",
            "provider_metadata_artifact_id": "A", "model_input_artifact_id": "B",
            "model_output_artifact_id": "C", "declaration_artifact_id": "D",
        }]
        with self.assertRaisesRegex(IntakeError, "NOT_RUN"):
            validate_manifest(rec, registry())

    @unittest.skipUnless(hasattr(os, "symlink"), "symbolic links unavailable")
    def test_symlink_artifact_bytes_are_not_opened(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "outside.txt").write_bytes(b"do not follow symlinks")
            (root / "link.txt").symlink_to(root / "outside.txt")
            rec = manifest()
            rec["artifacts"] = [artifact(
                "link.txt", sha256=hashlib.sha256(b"do not follow symlinks").hexdigest(),
            )]
            out = preflight(rec, root, registry())
        self.assertEqual(out["artifact_inventory"][0]["byte_status"], "MISSING_OR_UNREADABLE")
        self.assertEqual(out["invalid_or_missing_byte_records"], 1)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "POSIX FIFO unavailable")
    def test_fifo_manifest_rejected_without_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "manifest.fifo"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(IntakeError, "regular file"):
                load_manifest(fifo)

    def test_duplicate_json_field_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text('{"x":"one","x":"two"}', encoding="utf-8")
            with self.assertRaisesRegex(IntakeError, "duplicate JSON field"):
                load_manifest(path)


if __name__ == "__main__":
    unittest.main()
