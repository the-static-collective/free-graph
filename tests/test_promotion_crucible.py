import copy
import importlib.util
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "promotion_crucible.py"
CASE_PATH = ROOT / "specimens" / "promotion-crucible-v0" / "case.json"
POISON_SCRIPT_PATH = CASE_PATH.parent / "poison_consumer.py"


def load_crucible():
    if not SCRIPT_PATH.exists():
        raise AssertionError("promotion_crucible.py must implement the behavior-first evaluator")
    spec = importlib.util.spec_from_file_location("promotion_crucible", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_poison_consumer():
    if not POISON_SCRIPT_PATH.exists():
        raise AssertionError("poison_consumer.py must be a standalone reversed-behavior implementation")
    spec = importlib.util.spec_from_file_location("promotion_poison_consumer", POISON_SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def has_score_key(value):
    if isinstance(value, dict):
        return any("score" in key.lower() or has_score_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(has_score_key(item) for item in value)
    return False


class PromotionCrucibleTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads(CASE_PATH.read_text(encoding="utf-8"))

    def evaluate(self, case=None):
        crucible = load_crucible()
        return crucible.evaluate_case(case or self.case, CASE_PATH.parent)

    def test_projection_cannot_shrink_compatible_worlds_without_new_source(self):
        crucible = load_crucible()
        trace = {
            "id": "bad-shrink",
            "projection_event_id": "projection:bad-shrink",
            "compatible_worlds_before": ["world:a", "world:b"],
            "compatible_worlds_after": ["world:a"],
            "source_ids_before": ["source:one"],
            "source_ids_after": ["source:one"],
        }
        result = crucible.evaluate_trace("epistemic", trace)
        self.assertEqual("refuses", result["status"])

        trace["source_ids_after"].append("source:new-discriminator")
        result = crucible.evaluate_trace("epistemic", trace)
        self.assertEqual("satisfies", result["status"])

    def test_consequence_requires_separately_attributable_gate(self):
        crucible = load_crucible()
        ungated = {
            "id": "ungated",
            "projection_event_id": "projection:event",
            "state_before": "locked",
            "state_after": "unlocked",
            "gate_receipts": [],
        }
        self.assertEqual("refuses", crucible.evaluate_trace("consequence", ungated)["status"])

        gated = copy.deepcopy(ungated)
        gated["id"] = "gated"
        gated["gate_receipts"] = [{
            "id": "gate:owner-decision",
            "owner_world": "world:owner",
            "decision": "unlock",
        }]
        self.assertEqual("satisfies", crucible.evaluate_trace("consequence", gated)["status"])

    def test_projection_may_participate_in_lawful_causal_chain(self):
        receipt = self.evaluate()
        free_graph = next(item for item in receipt["consumer_results"] if item["id"] == "free-graph-relational-coordinate-v0")
        self.assertEqual("satisfies", free_graph["clauses"]["consequence"]["status"])
        self.assertEqual(2, free_graph["clauses"]["consequence"]["trace_count"])

    def test_decoder_change_cannot_rewrite_prior_projection(self):
        crucible = load_crucible()
        trace = copy.deepcopy(self.case["consumers"][0]["traces"]["historical"][0])
        trace["prior_projections_after"][0]["content_digest"] = "sha256:" + "9" * 64
        result = crucible.evaluate_trace("historical", trace)
        self.assertEqual("refuses", result["status"])

    def test_view_change_cannot_silently_change_object_identity(self):
        crucible = load_crucible()
        trace = copy.deepcopy(self.case["consumers"][0]["traces"]["identity"][0])
        trace["object_id_after"] = "object:other"
        result = crucible.evaluate_trace("identity", trace)
        self.assertEqual("refuses", result["status"])

    def test_same_words_reversed_behavior_poison_is_caught(self):
        receipt = self.evaluate()
        attack = receipt["attacks"][0]
        self.assertEqual("poison-copied-nouns-reversed-behavior", attack["consumer_id"])
        self.assertEqual("caught", attack["outcome"])
        self.assertEqual(["authority", "consequence"], attack["observed_refusals"])

        case = copy.deepcopy(self.case)
        poison = case["consumers"][2]
        poison["declared_policy"] = {
            "projectionAuthority": "absolutely-none",
            "projectionConsequence": "absolutely-gated",
        }
        changed = self.evaluate(case)
        self.assertEqual("caught", changed["attacks"][0]["outcome"])

    def test_poison_is_standalone_and_operationally_reverses_declaration(self):
        poison = load_poison_consumer()
        source = POISON_SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("free_graph", source)
        self.assertNotIn("scripts.fg", source)
        receipt = poison.run_poison_consumer()
        self.assertEqual("none", receipt["projectionAuthority"])
        self.assertEqual("owner-local", receipt["operationalTrace"]["effectiveWarrantAfter"])
        self.assertTrue(receipt["operationalTrace"]["actionUnlocked"])
        self.assertEqual("unlocked", receipt["operationalTrace"]["stateAfter"])
        self.assertEqual([], receipt["operationalTrace"]["gateReceipts"])
        committed = json.loads((CASE_PATH.parent / "poison-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(committed, receipt)

    def test_crucible_consumes_digest_pinned_poison_receipt(self):
        receipt = self.evaluate()
        pin = next(item for item in receipt["source_pins"] if item["consumer_id"] == "poison-copied-nouns-reversed-behavior")
        self.assertEqual(
            "3b054675a57ea2a4329d799d9e352e50cc61d112dc3383bd584106b3af5abaab",
            pin["native_receipt_sha256"],
        )
        poison = next(item for item in receipt["consumer_results"] if item["id"] == "poison-copied-nouns-reversed-behavior")
        self.assertEqual("native:poison:authority", poison["clauses"]["authority"]["traces"][0]["id"])
        self.assertEqual("native:poison:consequence", poison["clauses"]["consequence"]["traces"][0]["id"])

    def test_renamed_wrapper_is_not_materially_independent(self):
        case = copy.deepcopy(self.case)
        case["consumers"][1]["native_receipt"]["clauses"] = []
        wrapper = copy.deepcopy(case["consumers"][0])
        wrapper["id"] = "renamed-wrapper"
        wrapper["source"]["repository"] = "wrapper/example"
        wrapper["materiality"]["repository"] = "wrapper/example"
        wrapper["materiality"]["vocabulary_family"] = "renamed-words-v0"
        wrapper["materiality"]["receipt_shape"] = "renamed.receipt/v0"
        wrapper["traces"] = {"epistemic": wrapper["traces"]["epistemic"]}
        case["consumers"].append(wrapper)
        receipt = self.evaluate(case)
        self.assertEqual("only-one-domain", receipt["clauses"]["epistemic"]["verdict"])
        self.assertEqual(["free-graph-relational-coordinate-v0"], receipt["clauses"]["epistemic"]["independent_supports"])

    def test_different_native_vocabulary_supports_translation(self):
        receipt = self.evaluate()
        clause = receipt["clauses"]["epistemic"]
        self.assertEqual("supports", clause["verdict"])
        self.assertEqual(
            ["free-graph-relational-coordinate-v0", "national-treasure-ssw-math-001"],
            clause["independent_supports"],
        )
        native = (CASE_PATH.parent / "national-treasure-ssw-math-001.receipt.json").read_text(encoding="utf-8").lower()
        for word in ("projection", "authority", "constitutes", "gate"):
            self.assertNotIn(word, native)

    def test_clause_verdicts_do_not_average_into_green(self):
        receipt = self.evaluate()
        expected = self.case["expected"]["clauses"]
        actual = {name: result["verdict"] for name, result in receipt["clauses"].items()}
        self.assertEqual(expected, actual)
        self.assertEqual("split-required", receipt["whole"]["verdict"])
        self.assertIsNone(receipt["aggregate_score"])
        self.assertFalse(has_score_key({key: value for key, value in receipt.items() if key != "aggregate_score"}))

    def test_split_required_returns_productive_missing_discriminators(self):
        receipt = self.evaluate()
        for name in ("authority", "consequence", "historical"):
            clause = receipt["clauses"][name]
            self.assertEqual("only-one-domain", clause["verdict"])
            self.assertTrue(clause["semantic_fracture"])
            self.assertTrue(clause["missing_discriminator"])

    def test_native_receipt_digest_is_enforced(self):
        case = copy.deepcopy(self.case)
        case["consumers"][1]["native_receipt"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "native receipt digest mismatch"):
            self.evaluate(case)

    def test_cli_is_deterministic(self):
        crucible = load_crucible()
        with tempfile.TemporaryDirectory() as directory:
            first = pathlib.Path(directory) / "first.json"
            second = pathlib.Path(directory) / "second.json"
            self.assertEqual(0, crucible.main([str(CASE_PATH), "--output", str(first)]))
            self.assertEqual(0, crucible.main([str(CASE_PATH), "--output", str(second)]))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                (CASE_PATH.parent / "receipt.json").read_bytes(),
                first.read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
