"""Core Free Graph v0 addressing and validation."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from typing import Any

SCHEMA = "free-graph.packet/v0"
MODES = {"re-enter", "metabolize", "prove", "seed"}
AUTHORITIES = {"none", "source-local", "owner-local"}
STATUSES = {"observed", "proposed", "unresolved", "tested", "supported", "refused", "superseded", "locally-adopted"}
SOURCE_CLASSES = {"conversation-witness", "direct-observation", "project-source", "research-source", "graph-packet", "specimen-receipt", "human-witness", "gate-receipt", "world-head", "connector-receipt", "unresolved-receipt"}
SOURCE_AUTHORITY = {"conversation-witness":"none","direct-observation":"source-local","project-source":"source-local","research-source":"source-local","graph-packet":"none","specimen-receipt":"source-local","human-witness":"source-local","gate-receipt":"owner-local","world-head":"owner-local","connector-receipt":"source-local","unresolved-receipt":"none"}
NODE_KINDS = {"encounter", "world", "artifact", "claim", "question", "test", "testimony", "receipt"}
CLAIM_CLASSES = {"factual", "inferential", "design", "perceptual", "mathematical", "operational"}
WITNESS_REQUIREMENTS = {"none", "machine", "human", "both", "owner-defined"}
VERBS = {"connects", "descends-from", "tests", "bears-on", "constitutes"}
FORBIDDEN_KEYS = {"current_truth", "global_truth", "globally_true", "authority_transfer"}
ID_PREFIX = {"source":"fgs","node":"fgn","link":"fgl"}

class PacketError(ValueError): pass

def load_packet(path: str|Path) -> dict[str,Any]:
    try: value=json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise PacketError(f"cannot read JSON packet {path}: {exc}") from exc
    if not isinstance(value,dict): raise PacketError("packet root must be an object")
    return value

def canonical_bytes(value:Any, omit_key:str|None=None)->bytes:
    value=copy.deepcopy(value)
    if omit_key and isinstance(value,dict): value.pop(omit_key,None)
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def record_id(kind:str, record:dict[str,Any])->str:
    return f"{ID_PREFIX[kind]}:sha256:{hashlib.sha256(canonical_bytes(record,'id')).hexdigest()}"

def packet_id(packet:dict[str,Any])->str:
    return f"fgp:sha256:{hashlib.sha256(canonical_bytes(packet,'packet_id')).hexdigest()}"

def _nonempty(v): return isinstance(v,str) and bool(v.strip())
def _digest(v):
    if not isinstance(v,str) or not v.startswith("sha256:") or len(v)!=71: return False
    try: int(v[7:],16)
    except ValueError: return False
    return v==v.lower()
def _id(v,prefix):
    if not isinstance(v,str) or not v.startswith(prefix+":sha256:") or len(v)!=len(prefix)+72: return False
    try: int(v.rsplit(":",1)[1],16)
    except ValueError: return False
    return v==v.lower()
def _forbidden(v,path,e):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in FORBIDDEN_KEYS: e.append(f"{path}.{k} is forbidden")
            _forbidden(x,f"{path}.{k}",e)
    elif isinstance(v,list):
        for i,x in enumerate(v): _forbidden(x,f"{path}[{i}]",e)
def _cycle(links):
    g={}
    for l in links:
        if l.get("verb")=="descends-from": g.setdefault(l.get("from"),[]).append(l.get("to"))
    visiting=set(); visited=set(); trail=[]
    def walk(n):
        if n in visiting: return trail[trail.index(n):]+[n]
        if n in visited: return None
        visiting.add(n); trail.append(n)
        for p in g.get(n,[]):
            c=walk(p)
            if c:return c
        trail.pop(); visiting.remove(n); visited.add(n)
    for n in sorted(g):
        c=walk(n)
        if c:return c

def validate_packet(p:dict[str,Any])->list[str]:
    e=[]; add=e.append; _forbidden(p,"$",e)
    if p.get("schema")!=SCHEMA:add(f"$.schema must equal {SCHEMA!r}")
    if not _nonempty(p.get("purpose")):add("$.purpose must be non-empty")
    modes=p.get("modes")
    if not isinstance(modes,list) or not modes:add("$.modes must be non-empty array"); modes=[]
    elif any(x not in MODES for x in modes):add("$.modes contains unknown mode")
    scope=p.get("scope")
    if not isinstance(scope,dict):add("$.scope must be object")
    else:
        if not _nonempty(scope.get("task")):add("$.scope.task must be non-empty")
        if not isinstance(scope.get("worlds"),list) or any(not isinstance(x,str) for x in scope.get("worlds",[])):add("$.scope.worlds must be string array")
    cut=p.get("task_world_cut"); status=None
    if not isinstance(cut,dict):add("$.task_world_cut must be object")
    else:
        status=cut.get("status")
        if status not in {"sufficient","unresolved","not-required"}:add("$.task_world_cut.status is invalid")
        if not isinstance(cut.get("selected_ids"),list):add("$.task_world_cut.selected_ids must be array")
        if not isinstance(cut.get("owner_head_source_ids",[]),list):add("$.task_world_cut.owner_head_source_ids must be array")
        if not isinstance(cut.get("omitted"),list):add("$.task_world_cut.omitted must be array")
        if not _nonempty(cut.get("rationale")):add("$.task_world_cut.rationale must be non-empty")
    if status=="unresolved" and ({"metabolize","prove"}&set(modes)):add("an unresolved Task World Cut is terminal")
    if ({"metabolize","prove"}&set(modes)) and status!="sufficient":add("metabolize/prove require sufficient Task World Cut")
    for k in ("sources","nodes","links","residual_fog","non_imports"):
        if not isinstance(p.get(k),list):add(f"$.{k} must be array")
    sources=p.get("sources",[]) if isinstance(p.get("sources"),list) else []; nodes=p.get("nodes",[]) if isinstance(p.get("nodes"),list) else []; links=p.get("links",[]) if isinstance(p.get("links"),list) else []
    sids=set()
    for i,s in enumerate(sources):
        q=f"$.sources[{i}]"
        if not isinstance(s,dict):add(q+" must be object");continue
        sid=s.get("id"); cls=s.get("source_class")
        if not _id(sid,"fgs"):add(q+".id is not canonical")
        elif sid in sids:add(q+".id duplicated")
        else:sids.add(sid)
        if cls not in SOURCE_CLASSES:add(q+".source_class invalid")
        if s.get("authority")!=SOURCE_AUTHORITY.get(cls):add(q+".authority incompatible with source_class")
        loc=s.get("locator")
        if not isinstance(loc,dict) or any(not _nonempty(loc.get(x)) for x in ("system","coordinate","revision","resolution")):add(q+".locator incomplete")
        if not _digest(s.get("digest")):add(q+".digest invalid")
        access,export=s.get("access"),s.get("export")
        if access not in {"public","private","restricted","unknown"}:add(q+".access invalid")
        if export not in {"portable","pointer-only","prohibited","unknown"}:add(q+".export invalid")
        body=_nonempty(s.get("excerpt")) or _nonempty(s.get("resolvable_pointer")); redacted=access in {"private","restricted"} and export in {"pointer-only","prohibited"} and _nonempty(s.get("redaction"))
        if not(body or redacted):add(q+" needs excerpt/pointer or lawful private redaction")
        if _id(sid,"fgs") and record_id("source",s)!=sid:add(q+".id does not match content")
    nids=set()
    for i,n in enumerate(nodes):
        q=f"$.nodes[{i}]"
        if not isinstance(n,dict):add(q+" must be object");continue
        nid=n.get("id")
        if not _id(nid,"fgn"):add(q+".id is not canonical")
        elif nid in nids:add(q+".id duplicated")
        else:nids.add(nid)
        if n.get("kind") not in NODE_KINDS:add(q+".kind invalid")
        if not _nonempty(n.get("label")):add(q+".label empty")
        if n.get("status") not in STATUSES:add(q+".status invalid")
        refs=n.get("source_ids")
        if not isinstance(refs,list) or not refs or any(x not in sids for x in refs):add(q+".source_ids invalid")
        if "claim_class" in n and n["claim_class"] not in CLAIM_CLASSES:add(q+".claim_class invalid")
        if "witness_requirement" in n and n["witness_requirement"] not in WITNESS_REQUIREMENTS:add(q+".witness_requirement invalid")
        if _id(nid,"fgn") and record_id("node",n)!=nid:add(q+".id does not match content")
    lids=set()
    for i,l in enumerate(links):
        q=f"$.links[{i}]"
        if not isinstance(l,dict):add(q+" must be object");continue
        lid=l.get("id"); verb=l.get("verb"); refs=l.get("source_ids",[]); auth=l.get("authority")
        if not _id(lid,"fgl"):add(q+".id is not canonical")
        elif lid in lids:add(q+".id duplicated")
        else:lids.add(lid)
        if l.get("from") not in nids or l.get("to") not in nids:add(q+" endpoints invalid")
        if verb not in VERBS:add(q+".verb invalid")
        if not _nonempty(l.get("qualifier")):add(q+".qualifier empty")
        if l.get("status") not in STATUSES:add(q+".status invalid")
        if not isinstance(refs,list) or not refs or any(x not in sids for x in refs):add(q+".source_ids invalid")
        if auth not in AUTHORITIES:add(q+".authority invalid")
        if verb!="constitutes" and auth=="owner-local":add(q+": only constitutes may carry owner-local authority")
        if verb=="bears-on":
            if l.get("bearing") not in {"supports","refuses","unresolved"}:add(q+".bearing required")
            if not any(next((s for s in sources if s.get("id")==x),{}).get("source_class")=="specimen-receipt" for x in refs):add(q+": bears-on requires specimen receipt")
        if verb=="constitutes":
            if auth!="owner-local" or l.get("outcome") not in {"adopts","refuses","defers"}:add(q+": invalid constitution")
            for f in ("owner_world","gate","receipt_source_id","world_head_source_id"):
                if not _nonempty(l.get(f)):add(f"{q}.{f} required")
        if _id(lid,"fgl") and record_id("link",l)!=lid:add(q+".id does not match content")
    c=_cycle(links)
    if c:add("descends-from cycle: "+" -> ".join(c))
    allids=sids|nids|lids
    if isinstance(cut,dict):
        for x in cut.get("selected_ids",[]):
            if x not in allids:add(f"Task World Cut references unknown record {x!r}")
        for x in cut.get("owner_head_source_ids",[]):
            if x not in sids:add(f"Task World Cut references unknown owner head {x!r}")
    pid=p.get("packet_id")
    if pid is not None and (not _id(pid,"fgp") or packet_id(p)!=pid):add("$.packet_id does not match content")
    return e
