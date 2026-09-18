import copy
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("body_overlap", ROOT / "scripts" / "body_overlap.py")
body_overlap = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(body_overlap)


def chart(world, occurrence, *, provides=None, needs=None, interfaces=None):
    return {
        "schema": "body.chart/v0",
        "owner": {"world": world, "occurrence": occurrence},
        "provides": provides or [],
        "needs": needs or [],
        "interfaces": interfaces or [],
        "measure": {"declared": [], "observed": []},
        "receipts": [],
        "residual_fog": [],
        "non_authorities": [],
    }


class BodyOverlapTests(unittest.TestCase):
    def test_exact_need_offer_and_interface_match(self):
        left = chart(
            "3rdi",
            "sha-left",
            provides=[{"kind": "projection", "protocol": "3rdi.field", "version": "v0"}],
            interfaces=[{
                "name": "projection-out",
                "direction": "emit",
                "kind": "projection",
                "protocol": "3rdi.field",
                "version": "v0",
            }],
        )
        right = chart(
            "consumer",
            "sha-right",
            needs=[{"kind": "projection", "protocol": "3rdi.field", "version": "v0"}],
            interfaces=[{
                "name": "projection-in",
                "direction": "accept",
                "kind": "projection",
                "protocol": "3rdi.field",
                "version": "v0",
            }],
        )

        receipt = body_overlap.compare_charts(left, right)

        self.assertEqual(1, len(receipt["need_offer_matches"]))
        self.assertEqual(1, len(receipt["exact_interfaces"]))
        self.assertEqual([], receipt["adapter_candidates"])
        self.assertEqual("none", receipt["authority"])
        self.assertIn("receipt != constitutes", receipt["non_promotions"])

    def test_same_kind_incompatible_version_is_adapter_not_exact(self):
        left = chart(
            "left",
            "sha-left",
            interfaces=[{
                "name": "same-label",
                "direction": "emit",
                "kind": "projection",
                "protocol": "field",
                "version": "v1",
            }],
        )
        right = chart(
            "right",
            "sha-right",
            interfaces=[{
                "name": "same-label",
                "direction": "accept",
                "kind": "projection",
                "protocol": "field",
                "version": "v2",
            }],
        )

        receipt = body_overlap.compare_charts(left, right)

        self.assertEqual([], receipt["exact_interfaces"])
        self.assertEqual(1, len(receipt["adapter_candidates"]))

    def test_shared_filename_does_not_create_semantic_match(self):
        left = chart(
            "left",
            "sha-left",
            interfaces=[{
                "name": "receipt.json",
                "direction": "emit",
                "kind": "projection",
                "protocol": "alpha",
                "version": "v0",
            }],
        )
        right = chart(
            "right",
            "sha-right",
            interfaces=[{
                "name": "receipt.json",
                "direction": "accept",
                "kind": "different-kind",
                "protocol": "alpha",
                "version": "v0",
            }],
        )

        receipt = body_overlap.compare_charts(left, right)

        self.assertEqual([], receipt["exact_interfaces"])
        self.assertEqual([], receipt["adapter_candidates"])

    def test_need_never_grants_authority(self):
        left = chart(
            "provider",
            "sha-provider",
            provides=[{"kind": "artifact", "protocol": "x", "version": "v0"}],
        )
        right = chart(
            "needer",
            "sha-needer",
            needs=[{"kind": "artifact", "protocol": "x", "version": "v0"}],
        )

        receipt = body_overlap.compare_charts(left, right)

        self.assertEqual(1, len(receipt["need_offer_matches"]))
        self.assertEqual("none", receipt["authority"])
        self.assertNotIn("constitutes", receipt)

    def test_missing_occurrence_is_invalid(self):
        value = chart("left", "sha-left")
        value["owner"]["occurrence"] = ""

        errors = body_overlap.validate_chart(value)

        self.assertTrue(any("occurrence" in error for error in errors))

    def test_receipt_is_deterministic(self):
        left = chart(
            "left",
            "sha-left",
            provides=[{"kind": "artifact", "protocol": "x", "version": "v0"}],
        )
        right = chart(
            "right",
            "sha-right",
            needs=[{"kind": "artifact", "protocol": "x", "version": "v0"}],
        )

        first = body_overlap.compare_charts(left, right)
        second = body_overlap.compare_charts(copy.deepcopy(left), copy.deepcopy(right))

        self.assertEqual(first, second)
        self.assertEqual(first["receipt_id"], second["receipt_id"])

    def test_duplicate_declarations_do_not_manufacture_multiple_matches(self):
        declaration = {"kind": "artifact", "protocol": "x", "version": "v0"}
        left = chart("left", "sha-left", provides=[declaration, copy.deepcopy(declaration)])
        right = chart("right", "sha-right", needs=[declaration, copy.deepcopy(declaration)])

        receipt = body_overlap.compare_charts(left, right)

        self.assertEqual(1, len(receipt["need_offer_matches"]))


if __name__ == "__main__":
    unittest.main()
