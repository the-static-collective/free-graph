"""Free Graph Reason-Space 001.

A generic, typed *projection* of a bounded reasoning episode into the existing
five-verb Free Graph packet grammar. This is not a sixth relation verb,
a universal solver, a live truth store, or a capability/authority grant.

An upstream source owner is responsible for warranting source content. Here,
all inputs are self-declared; a caller must independently verify their bytes.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import re
from typing import Any

from scripts.fg_core import (
    PacketError, packet_id, record_id, validate_packet,
)

TRAIL_SCHEMA = "free-graph.reason-trail/v0"
READ_MODES = ["re-enter"]
SOURCE_CLASSES = {"project-source", "research-source", "specimen-receipt"}
ROLES = {
    "question": "question",
    "hypothesis": "claim",
    "probe": "test",
    "finding": "receipt",
    "next": "question",
}
INSTRUMENTS = {"alex-evidence", "graft-source", "dogram-graph",
               "planz-plan", "playdeck-validator", "lsd-divergence"}
STATUSES = {"proposed", "unresolved", "observed", "tested", "refused", "supported"}
VERBS = {"connects", "descends-from", "tests", "bears-on"}
LENSES = {
    "all": set(ROLES),
    "evidence": {"question", "hypothesis", "probe", "finding"},
    "next": {"question", "finding", "next"},
}
KEY = re.compile(r"[a-z][a-z0-9_-]{0,55}\Z")
SHA256 = re.compile(r"sha256:[a-f0-9]{64}\Z")
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
# The portable example is intentionally public and narrow; a different
# source posture requires a separate source-owner export and review.
URI = re.compile(r"https://github\.com/the-static-collective/[A-Za-z0-9_.-]+/blob/[a-f0-9]{40}/[A-Za-z0-9_./-]+\Z")
MAX_SOURCES, MAX_EVENTS, MAX_LINKS = 12, 32, 64


def _check(ok: bool, code: str) -> None:
    if not ok:
        raise PacketError(code)


def _name(value: Any, maxlen: int = 240) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= maxlen and not any(
        ord(c) < 32 and c not in "\n\t" for c in value
    )


def _key(obj: dict, required: set[str]) -> None:
    _check(isinstance(obj, dict) and set(obj) == required, "UNEXPECTED_FIELDS")


def _status(value: str) -> bool:
    return value in STATUSES and value != "locally-adopted"


def convert(trail: dict[str, Any]) -> dict[str, Any]:
    """Project a source-identified reasoning trail; preserve evidence/status boundaries."""
    _key(trail, {"schema", "id", "title", "question", "observed_at",
                 "sources", "events", "relations", "fog"})
    _check(trail["schema"] == TRAIL_SCHEMA, "UNKNOWN_TRAIL_SCHEMA")
    _check(isinstance(trail["id"], str) and KEY.fullmatch(trail["id"]),
           "INVALID_TRAIL_ID")
    _check(all(_name(trail[x]) for x in ("title", "question", "observed_at")),
           "MISSING_TRAIL_DESCRIPTION")
    sources, events, relations = (trail[k] for k in ("sources", "events", "relations"))
    _check(isinstance(sources, list) and 1 <= len(sources) <= MAX_SOURCES
           and isinstance(events, list) and 2 <= len(events) <= MAX_EVENTS
           and isinstance(relations, list) and len(relations) <= MAX_LINKS,
           "TRAIL_SIZE_BUDGET")
    _check(isinstance(trail["fog"], list) and 1 <= len(trail["fog"]) <= 16
           and all(_name(x, 250) for x in trail["fog"]), "FOG_REQUIRED")

    output_sources: list[dict] = []
    by_key: dict[str, dict] = {}
    for src in sources:
        _key(src, {"key", "class", "uri", "revision", "digest", "coordinate"})
        _check(isinstance(src["key"], str) and KEY.fullmatch(src["key"])
               and src["key"] not in by_key, "DUPLICATE_OR_INVALID_SOURCE_KEY")
        _check(src["class"] in SOURCE_CLASSES
               and isinstance(src["uri"], str) and URI.fullmatch(src["uri"])
               and isinstance(src["revision"], str) and SHA40.fullmatch(src["revision"])
               and "/blob/" + src["revision"] + "/" in src["uri"]
               and isinstance(src["digest"], str) and SHA256.fullmatch(src["digest"])
               and _name(src["coordinate"], 180), "INVALID_PUBLIC_SOURCE_COORDINATE")
        rec = {
            "source_class": src["class"],
            "locator": {
                "system": "git",
                "coordinate": src["coordinate"],
                "revision": src["revision"],
                "resolution": "exact-declared-public-source",
                "uri": src["uri"],
            },
            "observed_at": trail["observed_at"],
            "acquisition": "source-owner-provided-pointer; receipt validation external",
            "digest": src["digest"],
            "resolvable_pointer": src["uri"],
            "access": "public", "export": "portable",
            "authority": "source-local",
            "extensions": {
                "verified_by_generic_converter": False,
                "source_role": "pointer-to-independently-verifiable-origin",
            },
        }
        rec["id"] = record_id("source", rec)
        output_sources.append(rec)
        by_key[src["key"]] = rec

    output_nodes: list[dict] = []
    event_to_node: dict[str, dict] = {}
    for event in events:
        _check(isinstance(event, dict) and
               set(event) in (
                   {"key", "role", "label", "status", "sources"},
                   {"key", "role", "label", "status", "sources", "instrument"},
               ), "UNEXPECTED_REASON_EVENT_FIELDS")
        key, role = event["key"], event["role"]
        if "instrument" in event:
            _check(role == "probe" and event["instrument"] in INSTRUMENTS,
                   "INVALID_EXPLICIT_INSTRUMENT")
        _check(isinstance(key, str) and KEY.fullmatch(key)
               and key not in event_to_node and role in ROLES
               and _name(event["label"])
               and _status(event["status"])
               and isinstance(event["sources"], list)
               and 1 <= len(event["sources"]) <= MAX_SOURCES
               and len(set(event["sources"])) == len(event["sources"])
               and all(s in by_key for s in event["sources"]), "INVALID_REASON_EVENT")
        node = {
            "kind": ROLES[role], "label": event["label"],
            "status": event["status"],
            "source_ids": sorted(by_key[s]["id"] for s in event["sources"]),
            "extensions": {
                "reason_role": role,
                "source_status_not_truth": True,
                "workspace_id": trail["id"],
            },
        }
        if "instrument" in event:
            node["extensions"]["instrument"] = event["instrument"]
        if role == "hypothesis":
            node["claim_class"] = "inferential"
            node["witness_requirement"] = "owner-defined"
        node["id"] = record_id("node", node)
        output_nodes.append(node)
        event_to_node[key] = node
    _check(sum(n["extensions"]["reason_role"] == "question" for n in output_nodes) == 1,
           "ONE_QUESTION_REQUIRED")

    output_links: list[dict] = []
    seen_rel = set()
    for rel in relations:
        _key(rel, {"from", "to", "verb", "qualifier", "status", "sources", "bearing"})
        _check(rel["from"] in event_to_node and rel["to"] in event_to_node
               and rel["verb"] in VERBS and _name(rel["qualifier"], 180)
               and _status(rel["status"])
               and isinstance(rel["sources"], list)
               and 1 <= len(rel["sources"]) <= MAX_SOURCES
               and len(set(rel["sources"])) == len(rel["sources"])
               and all(s in by_key for s in rel["sources"]), "INVALID_REASON_RELATION")
        _check(
            (rel["verb"] == "bears-on" and
             rel["bearing"] in {"supports", "refuses", "unresolved"} and
             any(by_key[s]["source_class"] == "specimen-receipt"
                 for s in rel["sources"]))
            or (rel["verb"] != "bears-on" and rel["bearing"] is None),
            "BEARING_REQUIRES_ACTUAL_SPECIMEN_SOURCE",
        )
        identity = (rel["from"], rel["to"], rel["verb"], rel["qualifier"])
        _check(identity not in seen_rel, "DUPLICATE_REASON_RELATION")
        seen_rel.add(identity)
        link = {
            "from": event_to_node[rel["from"]]["id"],
            "to": event_to_node[rel["to"]]["id"],
            "verb": rel["verb"], "qualifier": rel["qualifier"],
            "status": rel["status"],
            "source_ids": sorted(by_key[s]["id"] for s in rel["sources"]),
            "authority": "none",
            "extensions": {"reason_relation_not_action_authority": True},
        }
        if rel["verb"] == "bears-on":
            link["bearing"] = rel["bearing"]
        link["id"] = record_id("link", link)
        output_links.append(link)

    # Re-enter and unresolved, never "prove" or owner-local action.
    packet = {
        "schema": "free-graph.packet/v0",
        "purpose": "Historical reasoning trail: " + trail["title"],
        "modes": READ_MODES,
        "scope": {
            "task": trail["question"],
            "worlds": ["free-graph", "motif"],
            "as_of": trail["observed_at"],
            "resolution": "historical-projection-not-project-canon",
        },
        "task_world_cut": {
            "status": "unresolved",
            "selected_ids": sorted(
                [r["id"] for r in [*output_sources, *output_nodes, *output_links]]
            ),
            "owner_head_source_ids": [],
            "omitted": [
                {"door": "owner-currentness",
                 "reason": "Source snapshots are not a current owner gate."},
                {"door": "external consequences",
                 "reason": "Tool outputs and plans do not imply real actions."},
            ],
            "rationale": "Question was investigated; owner acceptance and real-world "
                         "consequences remain unverified.",
        },
        "sources": output_sources,
        "nodes": output_nodes,
        "links": output_links,
        "residual_fog": list(trail["fog"]),
        "non_imports": [
            "No private record, credentials or owner-local gate receipt.",
            "No arbitrary native code execution or inferred causal genealogy.",
            "No conversion of source observation into project adoption.",
        ],
        "extensions": {
            "reason_space_version": TRAIL_SCHEMA,
            "trail_id": trail["id"],
            "lens": "all",
            "source_digests_must_be_verified_upstream": True,
            "owner_approval_implied": False,
        },
    }
    packet["packet_id"] = packet_id(packet)
    failures = validate_packet(packet)
    if failures:
        raise PacketError("INVALID_NATIVE_FREE_GRAPH_PACKET:\n" + "\n".join(failures))
    return packet


def lens(packet: dict[str, Any], name: str) -> dict[str, Any]:
    """Rotate an *interpretation/view*, keeping existing record IDs unchanged."""
    _check(name in LENSES, "UNKNOWN_REASON_LENS")
    failures = validate_packet(packet)
    _check(not failures, "SOURCE_PACKET_INVALID")
    include = LENSES[name]
    nodes = [deepcopy(n) for n in packet["nodes"]
             if n.get("extensions", {}).get("reason_role") in include]
    present = {n["id"] for n in nodes}
    links = [deepcopy(l) for l in packet["links"]
             if l["from"] in present and l["to"] in present]
    used = {sid for record in [*nodes, *links]
            for sid in record["source_ids"]}
    sources = [deepcopy(s) for s in packet["sources"] if s["id"] in used]
    result = deepcopy(packet)
    result["sources"], result["nodes"], result["links"] = sources, nodes, links
    result["purpose"] = f"{packet['purpose']} — {name} projection"
    result["task_world_cut"]["selected_ids"] = sorted([
        rec["id"] for rec in [*sources, *nodes, *links]
    ])
    result["task_world_cut"]["omitted"].append({
        "door": "lens-excluded-records",
        "reason": "This is an intentionally bounded projection, not a deletion or finding.",
    })
    result["extensions"]["lens"] = name
    result.pop("packet_id", None)
    result["packet_id"] = packet_id(result)
    failures = validate_packet(result)
    if failures:
        raise PacketError("INVALID_REASON_LENS:\n" + "\n".join(failures))
    return result


def pressure(packet: dict[str, Any]) -> dict[str, Any]:
    """Ask structural research questions from *unresolved claims*, not prose.

    This is neither an evidence adjudicator nor a tool-choice executive.
    Counting source-path edges never turns them into independent witnesses.
    """
    _check(not validate_packet(packet), "INVALID_REASON_PACKET_FOR_PRESSURE")
    _check(packet.get("extensions", {}).get("reason_space_version") == TRAIL_SCHEMA
           and packet["modes"] == READ_MODES
           and packet["task_world_cut"]["status"] == "unresolved",
           "ONLY_HISTORICAL_REASON_TRAILS_CAN_BE_PRESSURED")
    claims = [n for n in packet["nodes"]
              if n.get("extensions", {}).get("reason_role") == "hypothesis"
              and n["status"] in ("unresolved", "proposed")]
    results = []
    for node in sorted(claims, key=lambda x: x["id"]):
        tests = [l for l in packet["links"]
                 if l["to"] == node["id"] and l["verb"] == "tests"]
        bearings = [l for l in packet["links"]
                    if l["to"] == node["id"] and l["verb"] == "bears-on"]
        refused = [l for l in bearings if l["bearing"] == "refuses"]
        supported = [l for l in bearings if l["bearing"] == "supports"]
        unresolved = [l for l in bearings if l["bearing"] == "unresolved"]
        # These are observations about graph *records*. Distinct sources,
        # tests and verdicts must not be counted as independent facts.
        if supported and refused:
            gap = "CONFLICTED_RECORDED_BEARINGS"
            next_question = (
                "Which independent owner-scoped test could distinguish the "
                "recorded support from the recorded refusal?"
            )
        elif not supported:
            gap = "NO_RECORDED_SUPPORTING_SPECIMEN"
            next_question = (
                "What source-owned, reproducible positive specimen would "
                "actually support this claim, rather than merely connect to it?"
            )
        else:
            gap = "WARRANT_AND_OWNER_GATE_NOT_ESTABLISHED"
            next_question = (
                "Does the relevant source-owning world accept these "
                "recorded supporting specimens under its own gate?"
            )
        results.append({
            "hypothesis_node_id": node["id"],
            "historical_label": node["label"],
            "recorded_probe_edges": len(tests),
            "recorded_refusals": len(refused),
            "recorded_supports": len(supported),
            "recorded_unresolved_bearings": len(unresolved),
            "source_receipt_ids_not_independent_witness_count": sorted({
                sid for l in [*tests, *bearings] for sid in l["source_ids"]
            }),
            "gap_code": gap,
            "proposed_next_question": next_question,
            "claim_became_true": False,
            "owner_gate_satisfied": False,
            "tool_dispatch_authorized": False,
        })
    return {
        "schema": "free-graph.reason-pressure/v0",
        "source_packet_id": packet["packet_id"],
        "lens": packet["extensions"]["lens"],
        "status": "STRUCTURAL_QUESTIONS_NOT_DECISIONS",
        "candidates": results,
        "method": "bounded explicit graph-edge pattern; no semantic model or inference of source independence",
        "external_actions": False,
        "human_review_required": True,
        "automatic_authority": "NONE",
    }
