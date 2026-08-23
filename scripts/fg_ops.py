"""Free Graph v0 packet transformations. Projections never promote authority."""
from __future__ import annotations
import copy
from collections import deque
from .fg_core import PacketError, SCHEMA, canonical_bytes, packet_id, record_id, validate_packet

def rehash_packet(packet, stamp=False):
    v=copy.deepcopy(packet); v.pop("packet_id",None); sm={}; nm={}; lm={}
    for s in v.get("sources",[]):
        old=s.get("id")
        if not isinstance(old,str):raise PacketError("every source needs an id before rehash")
        s["id"]=record_id("source",s);sm[old]=s["id"]
    for n in v.get("nodes",[]):
        n["source_ids"]=[sm.get(x,x) for x in n.get("source_ids",[])];old=n.get("id")
        if not isinstance(old,str):raise PacketError("every node needs an id before rehash")
        n["id"]=record_id("node",n);nm[old]=n["id"]
    for l in v.get("links",[]):
        l["source_ids"]=[sm.get(x,x) for x in l.get("source_ids",[])]
        for f in ("receipt_source_id","world_head_source_id"):
            if f in l:l[f]=sm.get(l[f],l[f])
        for f in ("from","to","owner_world"):
            if f in l:l[f]=nm.get(l[f],l[f])
        old=l.get("id")
        if not isinstance(old,str):raise PacketError("every link needs an id before rehash")
        l["id"]=record_id("link",l);lm[old]=l["id"]
    ids={**sm,**nm,**lm};cut=v.get("task_world_cut")
    if isinstance(cut,dict):
        cut["selected_ids"]=[ids.get(x,x) for x in cut.get("selected_ids",[])]
        cut["owner_head_source_ids"]=[sm.get(x,x) for x in cut.get("owner_head_source_ids",[])]
    if stamp:v["packet_id"]=packet_id(v)
    errors=validate_packet(v)
    if errors:raise PacketError("rehashed packet invalid:\n"+"\n".join("- "+x for x in errors))
    return v

def neighbors(packet,node_id,depth=1):
    nids={n["id"] for n in packet["nodes"]}
    if node_id not in nids:raise PacketError(f"unknown node {node_id!r}")
    adj={n:[] for n in nids}
    for l in packet["links"]:adj[l["from"]].append(l);adj[l["to"]].append(l)
    seen={node_id};linkids=set();q=deque([(node_id,0)])
    while q:
        n,d=q.popleft()
        if d>=depth:continue
        for l in adj[n]:
            linkids.add(l["id"]);other=l["to"] if l["from"]==n else l["from"]
            if other not in seen:seen.add(other);q.append((other,d+1))
    ns=[n for n in packet["nodes"] if n["id"] in seen];ls=[l for l in packet["links"] if l["id"] in linkids];sids={x for r in [*ns,*ls] for x in r.get("source_ids",[])}
    out={"schema":SCHEMA,"purpose":f"Bounded neighborhood of {node_id}","modes":["re-enter"],"scope":copy.deepcopy(packet["scope"]),"task_world_cut":{"status":"sufficient","selected_ids":[r["id"] for r in [*ns,*ls]],"owner_head_source_ids":[x for x in packet["task_world_cut"].get("owner_head_source_ids",[]) if x in sids],"omitted":[{"door":"outside requested depth","reason":"bounded traversal"}],"rationale":f"Undirected neighborhood at depth {depth}; projection only."},"sources":[s for s in packet["sources"] if s["id"] in sids],"nodes":ns,"links":ls,"residual_fog":list(packet["residual_fog"]),"non_imports":list(packet["non_imports"]),"extensions":{"projection":"bounded-neighborhood","source_packet":packet.get("packet_id",packet_id(packet)),"depth":depth}}
    return rehash_packet(out)

def merge_packets(packets):
    def union(key):
        out={}
        for p in packets:
            for r in p[key]:
                rid=r["id"]
                if rid in out and canonical_bytes(out[rid])!=canonical_bytes(r):raise PacketError(f"conflicting immutable record {rid!r}")
                out[rid]=r
        return [out[k] for k in sorted(out)]
    out={"schema":SCHEMA,"purpose":f"Union projection of {len(packets)} immutable Free Graph packets","modes":["re-enter"],"scope":{"task":"Union projection; consult source packet purposes","worlds":sorted({w for p in packets for w in p["scope"]["worlds"]}),"resolution":"projection"},"task_world_cut":{"status":"not-required","selected_ids":[],"owner_head_source_ids":[],"omitted":[{"door":"owner-currentness","reason":"packet union cannot select current owner state"}],"rationale":"Set union performs no truth or authority promotion."},"sources":union("sources"),"nodes":union("nodes"),"links":union("links"),"residual_fog":sorted({x for p in packets for x in p["residual_fog"]}),"non_imports":sorted({x for p in packets for x in p["non_imports"]}),"extensions":{"projection":"packet-union","source_packets":[{"packet_id":p.get("packet_id",packet_id(p)),"purpose":p["purpose"]} for p in packets],"authority_effect":"none"}}
    errors=validate_packet(out)
    if errors:raise PacketError("generated invalid union:\n"+"\n".join("- "+x for x in errors))
    return out
