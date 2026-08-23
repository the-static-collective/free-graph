#!/usr/bin/env python3
"""Free Graph v0 CLI."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
if __package__ in {None,""}:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.fg_core import PacketError, canonical_bytes, load_packet, packet_id, validate_packet
from scripts.fg_ops import merge_packets, neighbors, rehash_packet

def checked(path):
    p=load_packet(path);e=validate_packet(p)
    if e:raise PacketError("\n".join("- "+x for x in e))
    return p

def dump(v,path=None):
    t=json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    Path(path).write_text(t,encoding="utf-8") if path else sys.stdout.write(t)
def validate(a):
    p=checked(a.packet);dump({"valid":True,"packet_id":packet_id(p),"sources":len(p["sources"]),"nodes":len(p["nodes"]),"links":len(p["links"])})
def canonicalize(a):sys.stdout.buffer.write(canonical_bytes(checked(a.packet))+b"\n")
def digest(a):sys.stdout.write(packet_id(checked(a.packet))+"\n")
def stamp(a):
    p=checked(a.packet);p["packet_id"]=packet_id(p);dump(p,a.output)
def rehash(a):dump(rehash_packet(load_packet(a.packet),a.stamp),a.output)
def neigh(a):dump(neighbors(checked(a.packet),a.node_id,a.depth),a.output)
def merge(a):dump(merge_packets([checked(x) for x in a.packets]),a.output)
def parser():
    r=argparse.ArgumentParser(description=__doc__);s=r.add_subparsers(dest="command",required=True)
    for name,fn in (("validate",validate),("canonicalize",canonicalize),("digest",digest)):
        p=s.add_parser(name);p.add_argument("packet");p.set_defaults(func=fn)
    p=s.add_parser("stamp");p.add_argument("packet");p.add_argument("--output");p.set_defaults(func=stamp)
    p=s.add_parser("rehash");p.add_argument("packet");p.add_argument("--stamp",action="store_true");p.add_argument("--output");p.set_defaults(func=rehash)
    p=s.add_parser("neighbors");p.add_argument("packet");p.add_argument("node_id");p.add_argument("--depth",type=int,default=1);p.add_argument("--output");p.set_defaults(func=neigh)
    p=s.add_parser("merge");p.add_argument("packets",nargs="+");p.add_argument("--output");p.set_defaults(func=merge)
    return r
def main():
    a=parser().parse_args()
    if getattr(a,"depth",0)<0:sys.stderr.write("error: --depth must be non-negative\n");return 2
    try:a.func(a)
    except PacketError as exc:sys.stderr.write(f"error:\n{exc}\n");return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
