import copy
import hashlib
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fg", ROOT / "scripts" / "fg.py")
fg = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(fg)


def digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def minimal_packet():
    excerpt = "witness"
    source = {
        "id": "tmp-source",
        "source_class": "direct-observation",
        "locator": {
            "system": "test",
            "container": "fixture",
            "coordinate": "line 1",
            "revision": "fixture-v1",
            "resolution": "exact",
        },
        "observed_at": "2026-08-23",
        "acquisition": "unit-test",
        "excerpt": excerpt,
        "digest": digest(excerpt),
        "access": "public",
        "export": "portable",
        "authority": "source-local",
    }
    node = {
        "id": "tmp-node",
        "kind": "artifact",
        "label": "fixture",
        "status": "observed",
        "source_ids": ["tmp-source"],
    }
    packet = {
        "schema": "free-graph.packet/v0",
        "purpose": "fixture",
        "modes": ["seed"],
        "scope": {"task": "fixture", "worlds": ["test"]},
        "task_world_cut": {
            "status": "sufficient",
            "selected_ids": ["tmp-source", "tmp-node"],
            "owner_head_source_ids": [],
            "omitted": [],
            "rationale": "fixture evidence is sufficient for seed-only behavior",
        },
        "sources": [source],
        "nodes": [node],
        "links": [],
        "residual_fog": [],
        "non_imports": [],
    }
    return fg.rehash_packet(packet, stamp=True)


class FreeGraphContractTests(unittest.TestCase):
    def test_minimal_packet_validates(self):
        packet = minimal_packet()
        self.assertEqual([], fg.validate_packet(packet))

    def test_private_redacted_source_can_be_digest_only(self):
        packet = minimal_packet()
        source = packet["sources"][0]
        source.pop("excerpt")
        source["access"] = "private"
        source["export"] = "pointer-only"
        source["redaction"] = "private excerpt intentionally omitted from public packet"
        source["id"] = "tmp-source"
        packet["nodes"][0]["source_ids"] = ["tmp-source"]
        packet["nodes"][0]["id"] = "tmp-node"
        packet["task_world_cut"]["selected_ids"] = ["tmp-source", "tmp-node"]
        packet.pop("packet_id", None)
        packet = fg.rehash_packet(packet, stamp=True)
        self.assertEqual([], fg.validate_packet(packet))

    def test_public_source_still_requires_excerpt_or_pointer(self):
        packet = minimal_packet()
        source = packet["sources"][0]
        source.pop("excerpt")
        source["redaction"] = "not enough for a public source"
        source["id"] = "tmp-source"
        packet["nodes"][0]["source_ids"] = ["tmp-source"]
        packet["nodes"][0]["id"] = "tmp-node"
        packet["task_world_cut"]["selected_ids"] = ["tmp-source", "tmp-node"]
        packet.pop("packet_id", None)
        with self.assertRaises(fg.PacketError):
            fg.rehash_packet(packet, stamp=True)

    def test_connects_never_claims_owner_local_authority(self):
        packet = minimal_packet()
        packet["nodes"].append({
            "id": "tmp-node-2",
            "kind": "artifact",
            "label": "fixture 2",
            "status": "observed",
            "source_ids": [packet["sources"][0]["id"]],
        })
        packet["links"].append({
            "id": "tmp-link",
            "from": packet["nodes"][0]["id"],
            "to": "tmp-node-2",
            "verb": "connects",
            "qualifier": "test",
            "status": "observed",
            "source_ids": [packet["sources"][0]["id"]],
            "authority": "owner-local",
        })
        packet["sources"][0]["id"] = "tmp-source"
        packet["nodes"][0]["id"] = "tmp-node"
        packet["nodes"][0]["source_ids"] = ["tmp-source"]
        packet["nodes"][1]["source_ids"] = ["tmp-source"]
        packet["links"][0]["from"] = "tmp-node"
        packet["links"][0]["source_ids"] = ["tmp-source"]
        packet["task_world_cut"]["selected_ids"] = ["tmp-source", "tmp-node", "tmp-node-2", "tmp-link"]
        packet.pop("packet_id", None)
        with self.assertRaises(fg.PacketError):
            fg.rehash_packet(packet, stamp=True)

    def test_public_specimens_validate(self):
        for name in ("wav-space-v0.public.json", "bandcamp-pressure-v0.public.json"):
            packet = fg.load_packet(ROOT / "specimens" / name)
            self.assertEqual([], fg.validate_packet(packet), name)

    def test_public_specimens_do_not_embed_private_excerpts(self):
        for name in ("wav-space-v0.public.json", "bandcamp-pressure-v0.public.json"):
            packet = fg.load_packet(ROOT / "specimens" / name)
            for source in packet["sources"]:
                if source["access"] in {"private", "restricted"} and source["export"] in {"pointer-only", "prohibited"}:
                    self.assertNotIn("excerpt", source, f"{name}: {source['id']}")
                    self.assertTrue(source.get("redaction"))


if __name__ == "__main__":
    unittest.main()
