"""Free Graph Reason-Space 002 — graph-native *investigation proposal* selector.

A read-only, deterministic mapping from recorded hypotheses, tests, bearings
and explicitly scoped tool capabilities to follow-up proposals. No tool is
executed by this module. A graph edge is never permission, fact or capability.

LSD is a *non-executable divergence profile*: a way to propose alternative
hypotheses under a bounded human task cut; it is not an installed GitHub organ.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from scripts.fg_core import PacketError, validate_packet
from scripts.reason_space import TRAIL_SCHEMA, pressure

REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "research" / "reason-space-002" / "instruments.json"
)
INSTRUMENT_IDS = (
    "playdeck-validator", "graft-source", "alex-evidence",
    "dogram-graph", "planz-plan", "lsd-divergence"
)
GAP_CLASSES = {
    "NO_RECORDED_SUPPORTING_SPECIMEN",
    "CONFLICTED_RECORDED_BEARINGS",
    "WARRANT_AND_OWNER_GATE_NOT_ESTABLISHED"
}
PRIORITY = {
    "NO_RECORDED_SUPPORTING_SPECIMEN": (
        "playdeck-validator", "graft-source", "alex-evidence",
        "lsd-divergence", "dogram-graph", "planz-plan"),
    "CONFLICTED_RECORDED_BEARINGS": (
        "alex-evidence", "graft-source", "playdeck-validator",
        "lsd-divergence", "dogram-graph", "planz-plan"),
    "WARRANT_AND_OWNER_GATE_NOT_ESTABLISHED": (
        "alex-evidence", "planz-plan", "graft-source",
        "playdeck-validator", "dogram-graph", "lsd-divergence"),
}
MODES = {"human_research_only", "not_required"}

def require(cond: bool, code: str):
    if not cond:
        raise PacketError(code)

def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    raw = Path(path).read_bytes()
    require(100 < len(raw) < 16000, "REGISTRY_SIZE_INVALID")
    o = json.loads(raw)
    require(o.get("schema") == "free-graph.inquiry-instruments/v0"
            and o.get("policy") == "CATALOG_ONLY_NO_AUTOMATIC_EXECUTION"
            and len(o.get("instruments", [])) == len(INSTRUMENT_IDS)
            and {i.get("id") for i in o["instruments"]} == set(INSTRUMENT_IDS)
            and all(value is False for value in o["permissions"].values()),
            "REGISTRY_AUTHORITY_MISMATCH")
    for i in o["instruments"]:
        require(i.get("mode") and i.get("availability")
                and i.get("evidence", "").startswith(
                    "https://github.com/the-static-collective/")
                and isinstance(i.get("constraints"), list)
                and len(i["constraints"]) >= 1, "REGISTRY_PROFILE_UNVERIFIED")
    lsd = next(i for i in o["instruments"]
               if i["id"] == "lsd-divergence")
    require(lsd["availability"] == "NOT_CONNECTED_AS_SOURCE_OWNED_EXECUTABLE"
            and lsd["mode"] == "HUMAN_REVIEWED_IDEATION_PROFILE_ONLY"
            and lsd["owner"] == "UNVERIFIED_EXECUTABLE_REPO",
            "LSD_CANNOT_CLAIM_GITHUB_EXECUTABILITY")
    return o

def task_cut(packet: dict, *, requested_profiles: list[str],
             source_scope_changed: bool = False,
             original_positive_specimen_available: bool = False,
             ideation_requested: bool = False,
             mode: str = "human_research_only") -> dict:
    """Operator-defined scope; never infer permission from graph content."""
    return {
        "schema": "free-graph.inquiry-task-cut/v0",
        "packet_id": packet["packet_id"],
        "requested_profiles": requested_profiles,
        "new_source_scope_provided": source_scope_changed,
        "original_positive_specimen_available": original_positive_specimen_available,
        "ideation_requested": ideation_requested,
        "mode": mode,
        "external_execution_permission": False,
        "owner_gate_permission": False,
        "private_repository_permission": False,
    }

def select(packet: dict[str, Any], task: dict[str, Any],
           registry: dict[str, Any] | None = None) -> dict:
    if registry is None:
        registry = load_registry()
    else:
        # Only a schema-valid registry, not a caller's alternative authority,
        # may describe tools.
        require(registry == load_registry(), "UNPINNED_PROFILE_REGISTRY")
    require(not validate_packet(packet)
            and packet.get("extensions", {}).get("reason_space_version")
                == TRAIL_SCHEMA
            and packet["task_world_cut"]["status"] == "unresolved",
            "INVALID_REASON_PACKET")
    require(type(task) is dict and set(task) == {
        "schema", "packet_id", "requested_profiles",
        "new_source_scope_provided",
        "original_positive_specimen_available", "ideation_requested",
        "mode", "external_execution_permission",
        "owner_gate_permission", "private_repository_permission"
    }, "INVALID_TASK_CUT_FIELDS")
    require(task["schema"] == "free-graph.inquiry-task-cut/v0"
            and task["packet_id"] == packet["packet_id"]
            and task["mode"] in MODES
            and all(task[f] is False for f in (
                "external_execution_permission", "owner_gate_permission",
                "private_repository_permission"))
            and all(type(task[f]) is bool for f in (
                "new_source_scope_provided",
                "original_positive_specimen_available", "ideation_requested"))
            and type(task["requested_profiles"]) is list
            and 1 <= len(task["requested_profiles"]) <= 6
            and len(set(task["requested_profiles"])) ==
                len(task["requested_profiles"])
            and set(task["requested_profiles"]) <= set(INSTRUMENT_IDS),
            "TASK_GRANTS_AUTHORITY_OR_INVALID_SCOPE")

    p = pressure(packet)
    source_profiles = {
        n["extensions"]["instrument"]
        for n in packet["nodes"] if
        n.get("extensions", {}).get("reason_role") == "probe"
        and n.get("extensions", {}).get("instrument") in INSTRUMENT_IDS
    }
    profiles = {x["id"]: x for x in registry["instruments"]}
    candidates = []
    for claim in p["candidates"]:
        gap = claim["gap_code"]
        require(gap in GAP_CLASSES, "UNKNOWN_INQUIRY_GAP")
        options = []
        for instrument in PRIORITY[gap]:
            if instrument not in task["requested_profiles"]:
                continue
            profile = profiles[instrument]
            if instrument == "lsd-divergence":
                state = ("HUMAN_ONLY_IDEATION_NOT_EXECUTABLE"
                         if task["ideation_requested"] and
                         task["mode"] == "human_research_only"
                         else "HOLD_IDEATION_NOT_REQUESTED")
                required = ["Human chooses whether to explore alternative frames",
                            "Any candidate remains proposed and separately testable"]
            elif instrument == "playdeck-validator":
                state = ("CAN_PROPOSE_OWNER_VALIDATION"
                         if task["original_positive_specimen_available"]
                         else "HOLD_NO_ORIGINAL_POSITIVE_SPECIMEN")
                required = ["Original rendered full-performance receipt",
                            "Source-owner PlayDeck validator and separate approval"]
            elif instrument == "graft-source":
                state = ("CAN_PROPOSE_NEW_BOUNDED_SOURCE_INSPECTION"
                         if task["new_source_scope_provided"]
                         else "HOLD_NEW_PUBLIC_SOURCE_SCOPE_REQUIRED")
                required = ["A genuinely new and allowed public source scope",
                            "No automatic network reads or third-party actions"]
            elif instrument == "alex-evidence":
                state = ("CAN_PROPOSE_EVIDENCE_ADJUDICATION"
                         if task["original_positive_specimen_available"]
                         or (gap == "CONFLICTED_RECORDED_BEARINGS"
                             and task["new_source_scope_provided"])
                         else "HOLD_NO_NEW_EVIDENCE_PATH")
                required = ["Independent attributable evidence path",
                            "Original ALEX proof/refusal semantics"]
            elif instrument == "dogram-graph":
                state = "HOLD_GRAPH_QUESTION_NOT_SELECTED"
                required = ["Explicit graph-model hypothesis and negative control"]
            elif instrument == "planz-plan":
                state = "HOLD_ACTION_SCHEMAS_NOT_SELECTED"
                required = ["Explicit finite task schema and candidate action effects"]
            else:
                raise PacketError("UNLISTED_INSTRUMENT")
            options.append({
                "instrument": instrument, "owner": profile["owner"],
                "prior_probe_recorded": instrument in source_profiles,
                "prior_probe_is_not_new_evidence":
                    instrument in source_profiles,
                "proposal_status": state, "source_evidence": profile["evidence"],
                "original_capability_contract": profile["operation"],
                "conditions_for_next_step": required,
                "does_not_assert_success": True,
                "tool_called": False,
                "external_execution_allowed": False,
                "source_owner_approval": False,
                "non_executable_ideation":
                    instrument == "lsd-divergence",
            })
        executable_route = next((x for x in options
            if x["proposal_status"].startswith("CAN_PROPOSE")), None)
        candidates.append({
            "hypothesis_node_id": claim["hypothesis_node_id"],
            "gap_code": gap,
            "recorded_refusals": claim["recorded_refusals"],
            "recorded_supports": claim["recorded_supports"],
            "recorded_unresolved": claim["recorded_unresolved_bearings"],
            "decisive_question": claim["proposed_next_question"],
            "selected_proposal": executable_route["instrument"]
                                 if executable_route else None,
            "selection_means_action": False,
            "options": options,
            "unresolved_precondition": (
                "Find original source-owner evidence or declare a fresh, "
                "explicitly permitted source scope."
                if executable_route is None else None),
        })
    return {
        "schema": "free-graph.inquiry-selection/v0",
        "status": ("TASK_CUT_NOT_REQUIRED" if task["mode"] == "not_required"
                   else "PROPOSALS_ONLY"),
        "source_packet_id": packet["packet_id"],
        "source_task_cut": task,
        "source_reason_pressure": p["schema"],
        "known_prior_instrument_profiles": sorted(source_profiles),
        "claim_candidates": candidates if task["mode"] != "not_required" else [],
        "all_costs": "UNKNOWN_NOT_INVENTED",
        "no_external_actions": True,
        "no_live_repository_read": True,
        "no_automatic_tool_invocations": True,
        "no_model_training": True,
        "no_owner_canon_or_authority": True,
        "human_review_required": True,
    }
