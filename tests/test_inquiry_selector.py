"""Adversarial investigation selector, historical reuse and LSD non-promotion."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import unittest
from scripts.fg_core import PacketError, validate_packet
from scripts.reason_space import convert, lens
from scripts.inquiry_selector import select, task_cut, load_registry

REV="0"*40
URL="https://github.com/the-static-collective/MOTIF/blob/"+REV+"/test.json"

def packet(case="no_support",marked_prior=False):
 s={
  "key":"source","class":"specimen-receipt","uri":URL,
  "revision":REV,"digest":"sha256:"+hashlib.sha256(b"test bytes").hexdigest(),
  "coordinate":"MOTIF/test.json"
 }
 events=[
  {"key":"q","role":"question","label":"How do we check this?","status":"observed","sources":["source"]},
  {"key":"h","role":"hypothesis","label":"This unsupported adapter is real","status":"unresolved","sources":["source"]},
  {"key":"t","role":"probe","label":"Native public source inspection",
   "status":"tested","sources":["source"]},
  {"key":"f","role":"finding","label":"No authentic receipt was established",
   "status":"refused","sources":["source"]},
  {"key":"n","role":"next","label":"Ask for original evidence",
   "status":"proposed","sources":["source"]},
 ]
 if marked_prior:events[2]["instrument"]="graft-source"
 rel=[
  {"from":"q","to":"h","verb":"connects","qualifier":"test subject",
   "status":"proposed","sources":["source"],"bearing":None},
  {"from":"t","to":"h","verb":"tests","qualifier":"search",
   "status":"tested","sources":["source"],"bearing":None},
  {"from":"f","to":"h","verb":"bears-on","qualifier":"refused",
   "status":"refused","sources":["source"],"bearing":"refuses"}
 ]
 if case=="conflict":
  events.append({"key":"support","role":"finding",
   "label":"Opposing test suggests support","status":"supported",
   "sources":["source"]})
  rel.append({"from":"support","to":"h","verb":"bears-on",
   "qualifier":"source-owned opposing outcome",
   "status":"supported","sources":["source"],"bearing":"supports"})
 if case=="gate":
  rel[-1]["bearing"]="supports";rel[-1]["status"]="supported"
 t={"schema":"free-graph.reason-trail/v0","id":"test-select-1",
   "title":"Selectable trial","question":"What should we investigate?",
   "observed_at":"2026-11-05","sources":[s],"events":events,
   "relations":rel,"fog":["Unverified original receipt and owner gate."]}
 return convert(t)

class SelectionTests(unittest.TestCase):
 def test_no_source_positive_and_no_new_scope_means_no_tool_can_run(self):
  p=packet(marked_prior=True)
  cut=task_cut(p,requested_profiles=[
   "playdeck-validator","graft-source","alex-evidence","lsd-divergence"
  ],ideation_requested=True)
  o=select(p,cut)
  self.assertEqual(o["status"],"PROPOSALS_ONLY")
  self.assertIn("graft-source",o["known_prior_instrument_profiles"])
  v=o["claim_candidates"][0]
  self.assertEqual(v["gap_code"],"NO_RECORDED_SUPPORTING_SPECIMEN")
  self.assertIsNone(v["selected_proposal"])
  self.assertEqual([x["proposal_status"] for x in v["options"]],[
   "HOLD_NO_ORIGINAL_POSITIVE_SPECIMEN",
   "HOLD_NEW_PUBLIC_SOURCE_SCOPE_REQUIRED",
   "HOLD_NO_NEW_EVIDENCE_PATH",
   "HUMAN_ONLY_IDEATION_NOT_EXECUTABLE"])
  self.assertTrue(v["options"][-1]["non_executable_ideation"])
  self.assertFalse(o["no_automatic_tool_invocations"] is False)
  self.assertEqual(o["all_costs"],"UNKNOWN_NOT_INVENTED")
 def test_a_new_source_scope_can_make_graft_a_proposal_not_an_action(self):
  p=packet(marked_prior=True)
  cut=task_cut(p,requested_profiles=["graft-source","lsd-divergence"],
               source_scope_changed=True,ideation_requested=True)
  o=select(p,cut);v=o["claim_candidates"][0]
  self.assertEqual(v["selected_proposal"],"graft-source")
  self.assertTrue(v["options"][0]["prior_probe_recorded"])
  self.assertTrue(v["options"][0]["prior_probe_is_not_new_evidence"])
  self.assertFalse(v["options"][0]["tool_called"])
  self.assertFalse(v["options"][0]["external_execution_allowed"])
 def test_original_positive_specimen_prioritizes_owner_validation(self):
  p=packet()
  cut=task_cut(p,requested_profiles=[
   "playdeck-validator","alex-evidence","graft-source"],
   original_positive_specimen_available=True)
  v=select(p,cut)["claim_candidates"][0]
  self.assertEqual(v["selected_proposal"],"playdeck-validator")
  self.assertEqual(v["options"][0]["proposal_status"],
                   "CAN_PROPOSE_OWNER_VALIDATION")
  self.assertFalse(v["options"][0]["source_owner_approval"])
 def test_disagreement_prefers_adjudication_only_if_new_evidence_exists(self):
  p=packet("conflict")
  no=select(p,task_cut(p,requested_profiles=["alex-evidence"]))
  yes=select(p,task_cut(p,requested_profiles=["alex-evidence"],
                       source_scope_changed=True))
  self.assertEqual(no["claim_candidates"][0]["gap_code"],
                   "CONFLICTED_RECORDED_BEARINGS")
  self.assertIsNone(no["claim_candidates"][0]["selected_proposal"])
  self.assertEqual(yes["claim_candidates"][0]["selected_proposal"],
                   "alex-evidence")
 def test_operator_not_required_can_decline_a_research_question(self):
  p=packet()
  v=select(p,task_cut(p,requested_profiles=["graft-source"],mode="not_required",
                      source_scope_changed=True))
  self.assertEqual(v["status"],"TASK_CUT_NOT_REQUIRED")
  self.assertEqual(v["claim_candidates"],[])
 def test_role_less_lens_does_not_invent_missing_hypotheses(self):
  p=packet()
  sub=lens(p,"next")
  self.assertEqual(select(sub,task_cut(sub,requested_profiles=["graft-source"]))[
    "claim_candidates"],[])
 def test_scope_cannot_smuggle_any_permission(self):
  p=packet()
  cut=task_cut(p,requested_profiles=["graft-source"])
  for key in ("external_execution_permission","owner_gate_permission",
              "private_repository_permission"):
   t=copy.deepcopy(cut);t[key]=True
   with self.assertRaisesRegex(PacketError,"TASK_GRANTS_AUTHORITY"):
    select(p,t)
  t=copy.deepcopy(cut);t["requested_profiles"]=["root-shell"]
  with self.assertRaisesRegex(PacketError,"TASK_GRANTS_AUTHORITY"):
   select(p,t)
  t=copy.deepcopy(cut);t["packet_id"]="fgp:sha256:"+"0"*64
  with self.assertRaisesRegex(PacketError,"TASK_GRANTS_AUTHORITY"):
   select(p,t)
  t=copy.deepcopy(cut);t["execute"]=True
  with self.assertRaisesRegex(PacketError,"INVALID_TASK_CUT_FIELDS"):
   select(p,t)
 def test_lsd_is_not_installed_source_owned_executable(self):
  r=load_registry()
  l=next(x for x in r["instruments"] if x["id"]=="lsd-divergence")
  self.assertEqual(l["owner"],"UNVERIFIED_EXECUTABLE_REPO")
  self.assertEqual(l["availability"],
                   "NOT_CONNECTED_AS_SOURCE_OWNED_EXECUTABLE")
  self.assertEqual(l["mode"],"HUMAN_REVIEWED_IDEATION_PROFILE_ONLY")
  bad=copy.deepcopy(r)
  next(x for x in bad["instruments"] if x["id"]=="lsd-divergence")[
   "availability"]="SOURCE_OWNED_EXECUTABLE"
  p=packet();c=task_cut(p,requested_profiles=["lsd-divergence"],
                        ideation_requested=True)
  with self.assertRaisesRegex(PacketError,"UNPINNED_PROFILE_REGISTRY"):
   select(p,c,bad)
 def test_instrument_metadata_is_not_permission_to_rename_hypothesis(self):
  p=packet(marked_prior=True)
  h=next(n for n in p["nodes"] if n.get("extensions",{}).get("reason_role")=="hypothesis")
  h["status"]="supported"  # no longer hash-valid
  with self.assertRaisesRegex(PacketError,"INVALID_REASON_PACKET"):
   select(p,task_cut(p,requested_profiles=["graft-source"]))
 def test_lsd_is_optional_not_forced_when_not_requested(self):
  p=packet()
  c=task_cut(p,requested_profiles=["lsd-divergence"])
  r=select(p,c)["claim_candidates"][0]["options"][0]
  self.assertEqual(r["proposal_status"],"HOLD_IDEATION_NOT_REQUESTED")
  self.assertFalse(r["tool_called"])

if __name__=="__main__":
 unittest.main()
