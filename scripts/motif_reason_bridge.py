#!/usr/bin/env python3
"""Convert one *real* source-pinned MOTIF native investigation to Free Graph.

MOTIF's original receipt is a Git-blob-pinned public artifact. The bridge
reads it as data; all conclusions are preserved as historical test outcomes,
never current truth, compatibility, canon, or owner-local authorization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.reason_space import TRAIL_SCHEMA, convert, lens
from scripts.fg_core import PacketError, validate_packet

MOTIF_COMMIT = "070aba60319cbab3d1c1838ec7481c350e7d86e5"
MOTIF_REPORT_PATH = (
    "fieldwork/map-of-maps-002/evidence/"
    "first-actual-native-court-2026-11-05.json"
)
MOTIF_BLOB = "457eaf895cc96cfa9f853b31ab665f38f2f3f0c9"
MOTIF_URL = (
    "https://github.com/the-static-collective/MOTIF/blob/"
    + MOTIF_COMMIT + "/" + MOTIF_REPORT_PATH
)


def _assert(ok: bool, why: str) -> None:
    if not ok:
        raise PacketError(why)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def translate(raw: bytes) -> dict:
    """Translate *only* a verified original public native report."""
    _assert(len(raw) <= 30000 and git_blob(raw) == MOTIF_BLOB,
            "HOLD_MOTIF_REPORT_BLOB_NOT_ORIGINAL")
    try:
        report = json.loads(raw)
        native = report["actual_observations"]
        # The checked-in MOTIF receipt is a verified, bounded *CI output
        # summary*, not the entire raw machine report. The full original
        # result is retained as an artifact at the cited workflow run.
        alex = native["ALEX"]
        plan = native["native_plan"]
        graft = native["GRAFT"]
        dogram = native["Dogram"]
        types = native["original_type_check"]
        next_probe = native["next_experiment"]
        map_question = (
            "Does a proposed planZ plan satisfy a PlayDeck "
            "rendered full-performance receipt contract?"
        )
    except (ValueError, KeyError, TypeError) as exc:
        raise PacketError("HOLD_REPORT_SCHEMA") from exc

    _assert(
        report["schema"] == "motif.map-002-first-source-owned-native-execution/v1"
        and report["status"] == native["status"]
        == "EXECUTED_NATIVE_READ_ONLY_RESEARCH_HELD"
        and report["effect"] == "none"
        and set(native["native_owners"]) == {"ALEX", "planZ", "GRAFT", "Dogram"}
        and len(native["native_owners"]) == 4
        and plan["plan_executed_by_planz"] is False
        and plan["external_actions"] == 0
        and graft["actual_network_gets"] == 0
        and len(graft["observed_docs"]) == 2
        and alex["attention_only_disposition"] == "REFUSE"
        and alex["attention_only_reason"] == "ATTENTION_NOT_SUPPORT"
        and alex["claim_admitted"] is False
        and dogram["forward_reachable_before"] is False
        and dogram["forward_reachable_after_counterfactual_edge"] is True
        and dogram["model_topology_only_not_adapter_compatibility"] is True
        and types["status"] == "HOLD_NO_EXECUTABLE_CAST"
        and types["actual_playdeck_validator_executed"] is False
        and next_probe["adapter_invented"] is False
        and next_probe["real_positive_witness_found"] is False,
        "HOLD_NATIVE_ORGAN_OR_AUTHORITY_INVARIANT",
    )

    sources = [{
        "key": "motif-run",
        "class": "specimen-receipt",
        "uri": MOTIF_URL,
        "revision": MOTIF_COMMIT,
        "digest": sha256(raw),
        "coordinate": "MOTIF/" + MOTIF_REPORT_PATH,
    }]
    for i, doc in enumerate(graft["observed_docs"], start=1):
        _assert(
            doc["source_url"].startswith(
                "https://github.com/the-static-collective/"
            )
            and doc["source_sha256"].startswith("sha256:"),
            "HOLD_UNVERIFIED_ORIGINAL_DOC_LOCUS",
        )
        # The original GRAFT replay verified these specific public source
        # bytes. The generic converter cannot independently re-fetch them.
        url = doc["source_url"]
        revision = url.split("/blob/")[1].split("/")[0]
        sources.append({
            "key": f"source-doc-{i}",
            "class": "research-source",
            "uri": url,
            "revision": revision,
            "digest": doc["source_sha256"],
            "coordinate": url.split("/the-static-collective/")[1],
        })

    events = [
        {"key": "question", "role": "question", "label": map_question,
         "status": "observed", "sources": ["motif-run"]},
        {"key": "hypothesis", "role": "hypothesis",
         "label": "Hypothesis under pressure: an unexecuted planZ proposal "
                  "can count as a rendered PlayDeck performance receipt",
         "status": "unresolved", "sources": ["motif-run"]},
        {"key": "plan-probe", "role": "probe",
         "label": f"Native planZ classical planner: {len(plan['actions'])} "
                  f"hypothetical research steps, declared cost "
                  f"{plan['declared_example_cost']}",
         "status": "tested", "sources": ["motif-run"]},
        {"key": "plan-finding", "role": "finding",
         "label": "A planned test is not an executed external step",
         "status": "observed", "sources": ["motif-run"]},
        {"key": "alex-probe", "role": "probe",
         "label": "ALEX asks whether a retrieved source establishes "
                  "an attributable SUPPORTS relation",
         "status": "tested", "sources": ["motif-run"]},
        {"key": "alex-finding", "role": "finding",
         "label": "ALEX: REFUSE / ATTENTION_NOT_SUPPORT",
         "status": "refused", "sources": ["motif-run"]},
        {"key": "dogram-probe", "role": "probe",
         "label": "Dogram checks reachability before and after an explicitly "
                  "hypothetical graph edge",
         "status": "tested", "sources": ["motif-run"]},
        {"key": "dogram-finding", "role": "finding",
         "label": "Hypothetical graph path becomes reachable; "
                  "software compatibility remains unproved",
         "status": "unresolved", "sources": ["motif-run"]},
        {"key": "graft-probe", "role": "probe",
         "label": "GRAFT's native public source scout in offline API replay",
         "status": "tested", "sources": ["motif-run", "source-doc-1",
                                       "source-doc-2"]},
        {"key": "graft-finding", "role": "finding",
         "label": "Two pinned public source documents observed; "
                  "no live GitHub search, no owner adoption",
         "status": "observed", "sources": ["motif-run", "source-doc-1",
                                         "source-doc-2"]},
        {"key": "type-probe", "role": "probe",
         "label": "Inspect original planZ proposal and PlayDeck receipt "
                  "source contracts; native PlayDeck validator not executed",
         "status": "observed", "sources": ["motif-run"]},
        {"key": "type-finding", "role": "finding",
         "label": "HOLD: a proposed plan is not proof of a rendered "
                  "full-performance receipt",
         "status": "refused", "sources": ["motif-run"]},
        {"key": "next", "role": "next", "label": next_probe["question"],
         "status": "proposed", "sources": ["motif-run"]},
    ]
    relationships = []
    def relation(left: str, right: str, verb: str, qualifier: str,
                 status: str, bearing=None) -> None:
        relationships.append({
            "from": left, "to": right, "verb": verb,
            "qualifier": qualifier, "status": status,
            "sources": ["motif-run"], "bearing": bearing,
        })

    relation("question", "hypothesis", "connects",
             "question proposes a bounded candidate for falsification",
             "proposed")
    for organ in ("plan", "alex", "dogram", "graft", "type"):
        relation(f"{organ}-probe", "hypothesis", "tests",
                 f"distinct source-owned {organ} method", "tested")
        relation(f"{organ}-finding", "hypothesis", "bears-on",
                 f"{organ} result is one scoped historical evaluation",
                 "refused" if organ in {"alex", "type"} else "unresolved",
                 "refuses" if organ in {"alex", "type"} else "unresolved")
        relation(f"{organ}-probe", f"{organ}-finding", "connects",
                 "the separate result belongs to this test only", "observed")
    relation("next", "question", "connects",
             "proposed follow-up, not an order to act", "proposed")

    fog = [
        "No actual rendered PlayDeck performance or positive validation was observed.",
        "A proposed plan cannot authenticate performance evidence.",
        "Graph reachability is not executable adapter compatibility.",
        "GRAFT's GitHub API calls were entirely replayed offline.",
        "This public historical record is not source-owner-current canon.",
        "No project accepted a new crossing or granted execution authority.",
    ]
    trail = {
        "schema": TRAIL_SCHEMA,
        "id": "motif-map002-first-native-court",
        "title": "MOTIF's original ALEX/planZ/Dogram/GRAFT investigation",
        "question": map_question,
        "observed_at": "2026-11-05",
        "sources": sources,
        "events": events,
        "relations": relationships,
        "fog": fog,
    }
    return trail


def build(raw: bytes, view: str = "all") -> dict:
    full = convert(translate(raw))
    return full if view == "all" else lens(full, view)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("motif_report", type=Path)
    parser.add_argument("--lens", choices=("all", "evidence", "next"),
                        default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        packet = build(args.motif_report.read_bytes(), args.lens)
        failures = validate_packet(packet)
        _assert(not failures, "HOLD_INVALID_PACKET")
        output = json.dumps(packet, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf8")
        else:
            print(output, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as err:
        print("HOLD_REASON_TRAIL:" + str(err)[:160], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
