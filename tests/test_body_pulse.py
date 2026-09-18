import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("body_pulse", ROOT / "scripts" / "body_pulse.py")
body_pulse = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(body_pulse)

SNAPSHOT = ROOT / "specimens" / "body-pulse-001" / "snapshot.json"


class BodyPulseTests(unittest.TestCase):
    def test_frozen_static_collective_pulse_is_deterministic(self):
        first = body_pulse.run_snapshot(SNAPSHOT)
        second = body_pulse.run_snapshot(SNAPSHOT)

        self.assertEqual(first, second)
        self.assertEqual(first["pulse_id"], second["pulse_id"])
        self.assertEqual(
            {
                "charts": 5,
                "pairwise_comparisons": 10,
                "exact_edges": 3,
                "adapter_edges": 0,
                "unmet_needs": 2,
                "isolated_charts": 1,
            },
            first["counts"],
        )
        self.assertEqual("none", first["authority"])
        self.assertIn("centrality != canon", first["non_promotions"])

    def test_frozen_pulse_matches_receipted_projection(self):
        generated = body_pulse.run_snapshot(SNAPSHOT)
        expected = json.loads(
            (SNAPSHOT.parent / "pulse.receipt.json").read_text(encoding="utf-8")
        )

        self.assertEqual(expected, generated)

    def test_frozen_pulse_exposes_expected_exact_seams(self):
        pulse = body_pulse.run_snapshot(SNAPSHOT)
        seams = {
            (edge["from_world"], edge["to_world"], edge["kind"])
            for edge in pulse["exact_edges"]
        }

        self.assertIn(
            ("the-static-collective/ALEX.2", "the-static-collective/LOADOUT", "current-organ-manifest"),
            seams,
        )
        self.assertIn(
            ("the-static-collective/3rdi", "the-static-collective/LOADOUT", "current-organ-manifest"),
            seams,
        )
        self.assertIn(
            ("the-static-collective/Dogram", "the-static-collective/ALEX.2", "calculation-receipt"),
            seams,
        )

    def test_self_provision_does_not_satisfy_neighbor_need(self):
        pulse = body_pulse.run_snapshot(SNAPSHOT)
        unmet = {
            (item["world"], item["kind"], item["protocol"], item["version"])
            for item in pulse["unmet_needs"]
        }

        self.assertIn(
            ("the-static-collective/free-graph", "graph-packet", "free-graph.packet", "v0"),
            unmet,
        )
        self.assertIn(
            ("the-static-collective/Dogram", "calculation-specimen", "dogram.specimen", "v0"),
            unmet,
        )

    def test_surface_digest_mismatch_refuses_snapshot(self):
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        snapshot["organs"][0]["surface_digest"] = "sha256:" + ("0" * 64)

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            for source in SNAPSHOT.parent.glob("*.surface.json"):
                (root / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            path = root / "snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")

            with self.assertRaises(body_pulse.BodyPulseError):
                body_pulse.run_snapshot(path)

    def test_surface_requires_no_authority(self):
        surface_path = SNAPSHOT.parent / "alex.surface.json"
        surface = json.loads(surface_path.read_text(encoding="utf-8"))
        surface["authority"] = "owner-local"

        errors = body_pulse.validate_surface(surface)

        self.assertTrue(any("authority" in error for error in errors))

    def test_owner_witness_detects_surface_drift_without_repair(self):
        surface = json.loads(
            (SNAPSHOT.parent / "3rdi.surface.json").read_text(encoding="utf-8")
        )
        before = copy.deepcopy(surface)
        occurrence = "a" * 40
        witness = {
            "schema": "body.owner-interface-witness/v0",
            "owner": surface["owner"],
            "occurrence": occurrence,
            "provides": [
                {
                    "kind": "new-owner-output",
                    "protocol": "owner.output",
                    "version": "v1",
                }
            ],
            "interfaces": [
                {
                    "name": "new-owner-output-out",
                    "direction": "emit",
                    "kind": "new-owner-output",
                    "protocol": "owner.output",
                    "version": "v1",
                }
            ],
            "evidence": [{"kind": "owner-code", "coordinate": "src/owner.py"}],
        }

        receipt = body_pulse.detect_surface_drift(surface, witness, occurrence)

        self.assertEqual("drift", receipt["status"])
        self.assertEqual(1, len(receipt["missing_provides"]))
        self.assertEqual(1, len(receipt["missing_interfaces"]))
        self.assertEqual("none", receipt["authority"])
        self.assertEqual(before, surface)
        self.assertIn("surface drift != auto-repair", receipt["non_promotions"])

    def test_snapshot_receipts_surface_drift_only_from_occurrence_matched_witness(self):
        surface = json.loads(
            (SNAPSHOT.parent / "3rdi.surface.json").read_text(encoding="utf-8")
        )
        occurrence = "b" * 40
        witness = {
            "schema": "body.owner-interface-witness/v0",
            "owner": surface["owner"],
            "occurrence": occurrence,
            "provides": [
                {
                    "kind": "new-owner-output",
                    "protocol": "owner.output",
                    "version": "v1",
                }
            ],
            "interfaces": [],
            "evidence": [{"kind": "owner-test", "coordinate": "test/owner.test.py"}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            surface_path = root / "surface.json"
            witness_path = root / "owner-witness.json"
            surface_path.write_text(json.dumps(surface), encoding="utf-8")
            witness_path.write_text(json.dumps(witness), encoding="utf-8")
            snapshot = {
                "schema": "body.snapshot/v0",
                "label": "SURFACE-DRIFT-TEST",
                "organs": [
                    {
                        "surface_path": "surface.json",
                        "surface_digest": body_pulse._sha256(surface),
                        "occurrence": occurrence,
                        "owner_witness_path": "owner-witness.json",
                        "owner_witness_digest": body_pulse._sha256(witness),
                    }
                ],
            }
            snapshot_path = root / "snapshot.json"
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

            pulse = body_pulse.run_snapshot(snapshot_path)
            self.assertEqual(1, pulse["counts"]["surface_drifts"])
            self.assertEqual("drift", pulse["surface_drift_receipts"][0]["status"])
            self.assertEqual("none", pulse["authority"])

            witness["occurrence"] = "c" * 40
            witness_path.write_text(json.dumps(witness), encoding="utf-8")
            snapshot["organs"][0]["owner_witness_digest"] = body_pulse._sha256(witness)
            snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")
            with self.assertRaises(body_pulse.BodyPulseError):
                body_pulse.run_snapshot(snapshot_path)

    def test_occurrence_binding_changes_chart_identity(self):
        surface = json.loads(
            (SNAPSHOT.parent / "3rdi.surface.json").read_text(encoding="utf-8")
        )

        first = body_pulse.derive_chart(surface, "a" * 40)
        second = body_pulse.derive_chart(copy.deepcopy(surface), "b" * 40)

        self.assertNotEqual(first["chart_id"], second["chart_id"])
        self.assertEqual(first["provides"], second["provides"])


if __name__ == "__main__":
    unittest.main()
