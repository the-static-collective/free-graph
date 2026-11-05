"""Reason-Space 001: source separation, identity, lens rotation and gates."""
from __future__ import annotations
import copy
import hashlib
from pathlib import Path
import unittest

from scripts.fg_core import PacketError, validate_packet, packet_id
from scripts.reason_space import TRAIL_SCHEMA, convert, lens
from scripts.motif_reason_bridge import build, MOTIF_BLOB, git_blob

REV="0"*40
URI=("https://github.com/the-static-collective/MOTIF/blob/"+REV+
     "/fieldwork/fixture.json")
def sample():
 return {
  "schema":TRAIL_SCHEMA,"id":"example-001",
  "title":"Two explanations; only one tested",
  "question":"Does the evidence justify a proposed connection?",
  "observed_at":"2026-11-05",
  "sources":[
   {"key":"receipt","class":"specimen-receipt",
    "uri":URI,"revision":REV,"coordinate":"MOTIF/fieldwork/fixture.json",
    "digest":"sha256:"+hashlib.sha256(b"actual local specimen bytes").hexdigest()},
   {"key":"source","class":"research-source",
    "uri":URI,"revision":REV,"coordinate":"MOTIF/fieldwork/fixture.json",
    "digest":"sha256:"+hashlib.sha256(b"source doc bytes").hexdigest()}
  ],
  "events":[
   {"key":"q","role":"question","label":"What happened?",
    "status":"observed","sources":["source"]},
   {"key":"h","role":"hypothesis","label":"A proposed relation might hold",
    "status":"unresolved","sources":["source"]},
   {"key":"t","role":"probe","label":"Check original tool's constraint",
    "status":"tested","sources":["receipt"]},
   {"key":"r","role":"finding","label":"Claim not supported",
    "status":"refused","sources":["receipt"]},
   {"key":"n","role":"next","label":"Retrieve independent evidence",
    "status":"proposed","sources":["source"]}
  ],
  "relations":[
   {"from":"q","to":"h","verb":"connects",
    "qualifier":"candidate hypothesis","status":"proposed",
    "sources":["source"],"bearing":None},
   {"from":"t","to":"h","verb":"tests",
    "qualifier":"independent source check","status":"tested",
    "sources":["receipt"],"bearing":None},
   {"from":"r","to":"h","verb":"bears-on",
    "qualifier":"refused by bounded check","status":"refused",
    "sources":["receipt"],"bearing":"refuses"},
   {"from":"n","to":"q","verb":"connects",
    "qualifier":"another question, not execution","status":"proposed",
    "sources":["source"],"bearing":None}
  ],
  "fog":["No independently authenticated owner acceptance."],
 }

class ReasonSpaceTests(unittest.TestCase):
 def test_native_free_graph_v0_not_a_new_graph_grammar(self):
  p=convert(sample())
  self.assertEqual(p["schema"],"free-graph.packet/v0")
  self.assertEqual(p["modes"],["re-enter"])
  self.assertEqual(p["task_world_cut"]["status"],"unresolved")
  self.assertEqual([],validate_packet(p))
  self.assertEqual(p["packet_id"],packet_id(p))
  self.assertEqual({l["verb"] for l in p["links"]},
                   {"connects","tests","bears-on"})
  self.assertTrue(all(l["authority"]=="none" for l in p["links"]))
  self.assertNotIn("constitutes",{l["verb"] for l in p["links"]})
  self.assertTrue(all(s["extensions"]["verified_by_generic_converter"] is False
                      for s in p["sources"]))
 def test_many_lenses_same_original_records_and_same_authority(self):
  p=convert(sample())
  a=lens(p,"evidence")
  b=lens(p,"next")
  self.assertNotEqual(p["packet_id"],a["packet_id"])
  self.assertNotEqual(a["packet_id"],b["packet_id"])
  all_nodes={n["id"] for n in p["nodes"]}
  self.assertTrue({n["id"] for n in a["nodes"]}.issubset(all_nodes))
  self.assertTrue({n["id"] for n in b["nodes"]}.issubset(all_nodes))
  self.assertTrue(any(n["extensions"]["reason_role"]=="next"
                      for n in b["nodes"]))
  self.assertFalse(any(n["extensions"]["reason_role"]=="next"
                       for n in a["nodes"]))
  for pr in (a,b):
   self.assertEqual([],validate_packet(pr))
   self.assertEqual(pr["task_world_cut"]["status"],"unresolved")
   self.assertTrue(all(l["authority"]=="none" for l in pr["links"]))
  self.assertTrue(all(n["id"] in all_nodes for n in b["nodes"]))
 def test_no_authority_or_sixth_verb_from_task_text(self):
  t=sample()
  t["relations"][0]["verb"]="authorizes"
  with self.assertRaisesRegex(PacketError,"INVALID_REASON_RELATION"):
   convert(t)
  t=sample()
  t["events"][1]["status"]="locally-adopted"
  with self.assertRaisesRegex(PacketError,"INVALID_REASON_EVENT"):
   convert(t)
  t=sample()
  t["events"][1]["status"]="globally_true"
  with self.assertRaisesRegex(PacketError,"INVALID_REASON_EVENT"):
   convert(t)
 def test_bears_on_requires_specimen_receipt_source(self):
  t=sample()
  t["relations"][2]["sources"]=["source"]
  with self.assertRaisesRegex(PacketError,"BEARING_REQUIRES"):
   convert(t)
 def test_no_private_content_through_convenient_generic_converter(self):
  t=sample()
  t["sources"][0]["uri"]="file:///home/person/secrets"
  with self.assertRaisesRegex(PacketError,"INVALID_PUBLIC_SOURCE"):
   convert(t)
  t=sample()
  t["sources"][0]["uri"]="https://evil.invalid/track/1"
  with self.assertRaisesRegex(PacketError,"INVALID_PUBLIC_SOURCE"):
   convert(t)
 def test_claim_change_changes_immutable_record_identity(self):
  a=convert(sample())
  changed=sample()
  changed["events"][1]["label"]="A different claim now"
  b=convert(changed)
  a_ids={x["id"] for x in a["nodes"]}
  b_ids={x["id"] for x in b["nodes"]}
  self.assertNotEqual(a_ids,b_ids)
  self.assertNotEqual(a["packet_id"],b["packet_id"])
 def test_lineage_cycle_is_rejected_by_existing_core(self):
  t=sample()
  t["relations"].extend([
   {"from":"q","to":"h","verb":"descends-from","qualifier":"counterfactual",
    "status":"proposed","sources":["source"],"bearing":None},
   {"from":"h","to":"q","verb":"descends-from","qualifier":"counterfactual",
    "status":"proposed","sources":["source"],"bearing":None}
  ])
  with self.assertRaisesRegex(PacketError,"descends-from cycle"):
   convert(t)
 def test_duplicated_or_out_of_scope_keys_fail(self):
  t=sample()
  t["events"].append(copy.deepcopy(t["events"][0]))
  with self.assertRaisesRegex(PacketError,"INVALID_REASON_EVENT"):
   convert(t)
  t=sample()
  t["send_to_all_connected_apps"]=True
  with self.assertRaisesRegex(PacketError,"UNEXPECTED_FIELDS"):
   convert(t)
 def test_source_digest_is_declaration_not_autoverified(self):
  t=sample()
  t["sources"][0]["digest"]="sha256:"+"f"*64
  p=convert(t)
  self.assertFalse(p["sources"][0]["extensions"]["verified_by_generic_converter"])
 def test_MOTIF_original_receipt_must_be_exact_git_blob(self):
  with self.assertRaisesRegex(PacketError,"HOLD_MOTIF_REPORT_BLOB"):
   build(b"{}")
  self.assertEqual(len(MOTIF_BLOB),40)

if __name__=="__main__":
 unittest.main()
