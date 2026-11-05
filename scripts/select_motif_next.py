#!/usr/bin/env python3
"""Use a verified MOTIF historical receipt with Free Graph's general selector.

No tool calls, no network, no filesystem writes (except explicitly requested
local output JSON). A human-provided new-source flag is a proposed task cut,
not independent proof that a new source exists or permission to browse it.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
if __package__ in (None,""):
 sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.motif_reason_bridge import build
from scripts.inquiry_selector import select, task_cut, INSTRUMENT_IDS

def main():
 p=argparse.ArgumentParser()
 p.add_argument("motif_report",type=Path)
 p.add_argument("--profiles",nargs="+",choices=INSTRUMENT_IDS,
  default=["playdeck-validator","graft-source","alex-evidence",
           "dogram-graph","planz-plan","lsd-divergence"])
 p.add_argument("--new-source-scope",action="store_true")
 p.add_argument("--original-positive-specimen",action="store_true")
 p.add_argument("--ideation",action="store_true")
 p.add_argument("--no-investigation",action="store_true")
 p.add_argument("--output",type=Path)
 args=p.parse_args()
 try:
  pckt=build(args.motif_report.read_bytes(),"all")
  cut=task_cut(pckt,requested_profiles=args.profiles,
   source_scope_changed=args.new_source_scope,
   original_positive_specimen_available=args.original_positive_specimen,
   ideation_requested=args.ideation,
   mode="not_required" if args.no_investigation else "human_research_only")
  out=select(pckt,cut)
  body=json.dumps(out,indent=2,sort_keys=True)+"\n"
  if args.output:args.output.write_text(body,encoding="utf8")
  else:sys.stdout.write(body)
  return 0
 except (OSError,ValueError,TypeError,KeyError) as error:
  sys.stderr.write("HOLD_INQUIRY_SELECTOR:"+str(error)[:170]+"\n")
  return 2

if __name__=="__main__":
 raise SystemExit(main())
