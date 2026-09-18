import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("body_pulse", ROOT / "scripts" / "body_pulse.py")
body_pulse = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(body_pulse)


class BodyStandardTests(unittest.TestCase):
    def test_free_graph_publishes_valid_owner_surface(self):
        path = ROOT / ".body" / "surface-v0.json"
        surface = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual([], body_pulse.validate_surface(surface))
        self.assertEqual("the-static-collective/free-graph", surface["owner"])
        self.assertEqual("owner-published", surface["publication"]["status"])
        self.assertEqual("none", surface["authority"])

    def test_surface_schema_preserves_no_authority_default(self):
        schema = json.loads(
            (ROOT / "schema" / "body-surface-v0.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual("body.surface/v0", schema["properties"]["schema"]["const"])
        self.assertEqual("none", schema["properties"]["authority"]["const"])
        for field in (
            "organ",
            "owner",
            "publication",
            "provides",
            "needs",
            "interfaces",
            "measure",
            "receipts",
            "residual_fog",
            "non_authorities",
            "evidence",
            "authority",
        ):
            self.assertIn(field, schema["required"])

    def test_exemption_schema_requires_explicit_reason(self):
        schema = json.loads(
            (ROOT / "schema" / "body-exemption-v0.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual("body.exemption/v0", schema["properties"]["schema"]["const"])
        self.assertIn("reason_code", schema["required"])
        self.assertIn("reason", schema["required"])
        self.assertIn("review_trigger", schema["required"])
        self.assertEqual("none", schema["properties"]["authority"]["const"])


if __name__ == "__main__":
    unittest.main()
