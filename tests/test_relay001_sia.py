import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.fg_core import validate_packet, packet_id
from scripts.fg_ops import neighbors, merge_packets
from scripts.relay001_sia import build_graph, sia_id, sha, SEQUENCE, ROLES, PacketError


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def make_fixture(root):
    vault = root / "vault"
    archive = root / "archive"
    vault.mkdir()
    archive.mkdir()
    contents = b"small synthetic fixture only\n"
    (archive / "source").mkdir()
    (archive / "source" / "song.mp3").write_bytes(contents)
    source = sha(contents)

    def save(obj):
        obj = dict(obj)
        obj["id"] = sia_id(obj)
        p = vault / "objects"
        p.mkdir(exist_ok=True)
        (p / (obj["id"][7:] + ".json")).write_bytes(json_bytes(obj))
        return obj

    observation = save({
        "schema": "sia/observation/v0",
        "artifact": {"externalId": "test", "kind": "song", "title": "Synthetic tone", "url": "https://example.invalid/song", "creator": "test"},
        "capture": {"observedAt": "2026-10-13T10:00:00Z", "method": "owner-export", "rights": "links-only",
                    "sourceUrl": "https://example.invalid/song", "evidenceUrl": "https://example.invalid/song", "notes": "synthetic"},
        "facts": [{"key": "audio_sha256", "value": source, "basis": "owner-note"}],
        "relations": [], "interpretations": []
    })
    entries = []
    previous = None
    for step, (organ, status) in enumerate(SEQUENCE, 1):
        evidence = []
        for role, relative in ROLES[organ].items():
            p = archive / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            raw = json_bytes({"role": role, "synthetic": True})
            p.write_bytes(raw)
            evidence.append({"role": role, "sha256": sha(raw), "mediaType": "application/json"})
        obj = save({
            "schema": "sia/relay-entry/v0",
            "missionId": "relay-001-synthetic",
            "sourceObservationId": observation["id"],
            "sourceMediaSha256": source,
            "step": step, "organ": organ, "status": status,
            "parents": [] if previous is None else [previous],
            "evidence": evidence,
            "verification": {"scope": "synthetic claim, not independently signed",
                             "mechanism": "local-fixture", "verified": True},
            "effect": "local-index" if organ == "SIA" else "local-read" if organ == "GHoT" else "none",
            "permissions": {"publication": False, "admission": False, "authorityTransferred": False}
        })
        entries.append({
            "step": step, "organ": organ, "status": status, "id": obj["id"],
            "parents": obj["parents"], "evidence": obj["evidence"],
            "verification": obj["verification"]
        })
        previous = obj["id"]
    index = {
        "schema": "sia/relay-index/v0",
        "missionId": "relay-001-synthetic",
        "title": "Synthetic tone",
        "sourceObservationId": observation["id"],
        "sourceMediaSha256": source,
        "entries": entries, "executedOrgans": 5, "projectCount": 39,
        "proposedRemaining": [
            {"project": "candidate-" + str(i), "lane": "test",
             "status": "PROPOSED_NOT_EXECUTED"} for i in range(34)
        ]
    }
    index_path = archive / "relay-index.json"
    index_path.write_bytes(json_bytes(index))
    return index_path, vault, archive


class SiaSixthOrganTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.index, self.vault, self.archive = make_fixture(Path(self.tmp.name))

    def graph(self):
        return build_graph(self.index, self.vault, self.archive)

    def test_pinned_sia_vault_to_native_free_graph(self):
        p = self.graph()
        self.assertEqual(validate_packet(p), [])
        self.assertEqual(packet_id(p), p["packet_id"])
        self.assertEqual(len(p["sources"]), 7)
        self.assertEqual(len(p["nodes"]), 45)
        self.assertEqual(len(p["links"]), 48)
        self.assertEqual(sum(n["status"]=="proposed" for n in p["nodes"]), 34)
        self.assertEqual(sum(l["verb"]=="descends-from" for l in p["links"]), 4)
        self.assertFalse(any(l["verb"]=="constitutes" or l["authority"]=="owner-local" for l in p["links"]))
        self.assertFalse(p["extensions"]["owner_admission"])
        self.assertTrue(p["extensions"]["exact_local_evidence_bytes_checked"])
        self.assertEqual(self.graph(), p)
        song = next(n["id"] for n in p["nodes"] if n["label"].endswith("· source"))
        near = neighbors(p, song, depth=1)
        self.assertEqual(validate_packet(near), [])
        self.assertEqual(len(near["nodes"]), 40)  # song, five stages, 34 candidates
        union = merge_packets([p, p])
        self.assertEqual(validate_packet(union), [])
        self.assertEqual(len(union["nodes"]), 45)

    def test_no_evidence_means_no_claim_of_verified_bytes(self):
        p = build_graph(self.index, self.vault)
        self.assertFalse(p["extensions"]["exact_local_evidence_bytes_checked"])
        self.assertEqual(validate_packet(p), [])

    def test_mutated_original_source_fails(self):
        (self.archive/"source"/"song.mp3").write_bytes(b"modified")
        with self.assertRaisesRegex(PacketError, "ORIGINAL_MEDIA_CHANGED"):
            self.graph()

    def test_mutated_evidence_refuses(self):
        p=self.archive/ROLES["reLATTE"]["signed-roundtrip"]
        p.write_bytes(b"tampered synthetic evidence")
        with self.assertRaisesRegex(PacketError, "EVIDENCE_BYTES_CHANGED"):
            self.graph()

    def test_stored_entry_tampering_refuses(self):
        index=json.loads(self.index.read_text())
        object_id=index["entries"][2]["id"]
        p=self.vault/"objects"/(object_id[7:]+".json")
        v=json.loads(p.read_text());v["status"]="ADMITTED"
        p.write_bytes(json_bytes(v))
        with self.assertRaisesRegex(PacketError, "SIA_OBJECT_DIGEST_INVALID"):
            self.graph()

    def test_invitation_is_not_execution(self):
        v=json.loads(self.index.read_text())
        v["proposedRemaining"][0]["status"]="EXECUTED"
        self.index.write_bytes(json_bytes(v))
        with self.assertRaisesRegex(PacketError, "PROPOSAL_ALREADY_EXECUTED"):
            self.graph()

    def test_parent_cannot_be_rewritten(self):
        v=json.loads(self.index.read_text())
        v["entries"][3]["parents"]=[]
        self.index.write_bytes(json_bytes(v))
        with self.assertRaisesRegex(PacketError,"RELAY_STAGE_DRIFT"):
            self.graph()

    def test_cannot_invent_owner_admission(self):
        index=json.loads(self.index.read_text())
        obj_id=index["entries"][2]["id"]
        p=self.vault/"objects"/(obj_id[7:]+".json")
        v=json.loads(p.read_text())
        v["permissions"]["admission"]=True
        v["id"]=sia_id(v)
        p.write_bytes(json_bytes(v))
        with self.assertRaises(PacketError):
            self.graph()


if __name__ == "__main__":
    unittest.main()
