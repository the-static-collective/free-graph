#!/usr/bin/env python3
"""SIA -> Free Graph, RELAY-001. Append-only projection; no authority promotion.

Only SIA's immutable local objects and a specifically supplied SIA index are
read. The upstream "verified" flag is historical testimony, not re-verification
of reLATTE signatures. Optional packet_root checks exact referenced bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fg_core import PacketError, packet_id, validate_packet
from scripts.fg_ops import neighbors, rehash_packet

SEQUENCE = [
    ("LOADOUT", "BOUND"),
    ("GHoT", "EXECUTED"),
    ("reLATTE", "RECEIVED_HELD"),
    ("webZ", "OBSERVED"),
    ("SIA", "INDEXED"),
]
ROLES = {
    "LOADOUT": {
        "loadout-binding": "crossing/native-song-evidence/loadout-binding.json",
        "loadout-parameters": "crossing/native-song-evidence/loadout-parameters.json",
    },
    "GHoT": {
        "ghot-task": "crossing/native-song-evidence/ghot-task.json",
        "ghot-receipt": "crossing/native-song-evidence/ghot-receipt.json",
        "ghot-execution": "crossing/native-song-evidence/relay-crossing.json",
    },
    "reLATTE": {
        "signed-roundtrip": "third-organ/public/roundtrip-result.json",
        "signed-transport": "third-organ/public/transport-bundle.json",
        "hold-verification": "third-organ/public/verification.json",
    },
    "webZ": {
        "observer-report": "fourth-organ/observation.json",
        "observer-mission": "fourth-organ/mission-fourth.json",
    },
    "SIA": {
        "source-seed": "seed.json",
        "mission-plan": "mission.json",
    },
}


def require(condition, message):
    if not condition:
        raise PacketError(message)


def sha(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def jcs_subset(v):
    """SIA v0 canonical subset: safe integral JSON numbers, sorted keys, UTF-8."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    if isinstance(v, int) and not isinstance(v, bool) and abs(v) <= 2**53 - 1:
        return str(v)
    if isinstance(v, list):
        return "[" + ",".join(jcs_subset(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(jcs_subset(k) + ":" + jcs_subset(v[k]) for k in sorted(v)) + "}"
    raise PacketError("SIA canonical payload contains unsupported value")


def sia_id(obj):
    body = {k: v for k, v in obj.items() if k != "id"}
    return sha((obj["schema"] + "\0" + jcs_subset(body)).encode("utf-8"))


def read_bounded(path, root, max_size=1024 * 1024):
    root = Path(root).resolve()
    p = Path(path).resolve()
    require(p.is_relative_to(root) and p.is_file(), "SOURCE_PATH_ESCAPES_ROOT")
    require(p.stat().st_size <= max_size, "SOURCE_TOO_LARGE")
    return p.read_bytes()


def read_json(path, root):
    raw = read_bounded(path, root)
    try:
        return json.loads(raw), raw
    except (ValueError, UnicodeDecodeError) as exc:
        raise PacketError("INVALID_JSON") from exc


def verify_index_and_vault(index_path, vault):
    index, index_bytes = read_json(index_path, Path(index_path).parent)
    require(index.get("schema") == "sia/relay-index/v0", "WRONG_SIA_INDEX")
    require(index.get("executedOrgans") == 5 and index.get("projectCount") == 39,
            "UNEXPECTED_RELAY_INVENTORY")
    require(isinstance(index.get("entries"), list) and len(index["entries"]) == 5,
            "EXPECTED_FIVE_SIA_EVENTS")
    proposed = index.get("proposedRemaining")
    require(isinstance(proposed, list) and len(proposed) == 34, "EXPECTED_34_UNEXECUTED_DOORS")
    seen = set()
    for p in proposed:
        require(isinstance(p, dict) and p.get("status") == "PROPOSED_NOT_EXECUTED"
                and isinstance(p.get("project"), str) and p["project"]
                and p["project"] not in seen and p["project"] not in [x[0] for x in SEQUENCE],
                "PROPOSAL_ALREADY_EXECUTED_OR_DUPLICATED")
        seen.add(p["project"])
    src_id = index.get("sourceObservationId")
    require(isinstance(src_id, str) and src_id.startswith("sha256:"),
            "INVALID_SOURCE_OBSERVATION_ID")
    source_sha = index.get("sourceMediaSha256")
    require(isinstance(source_sha, str) and len(source_sha) == 71,
            "INVALID_SOURCE_MEDIA_SHA")
    vault = Path(vault).resolve()
    def load(ident):
        require(isinstance(ident, str) and len(ident) == 71
                and ident[:7] == "sha256:"
                and all(c in "0123456789abcdef" for c in ident[7:]), "INVALID_SIA_ADDRESS")
        o, raw = read_json(vault / "objects" / (ident[7:] + ".json"), vault)
        require(o.get("id") == ident and sia_id(o) == ident, "SIA_OBJECT_DIGEST_INVALID")
        return o, raw
    src, src_bytes = load(src_id)
    require(src.get("schema") == "sia/observation/v0" and
            src.get("artifact", {}).get("kind") == "song" and
            src.get("artifact", {}).get("title") == index.get("title") and
            any(f.get("key") == "audio_sha256" and f.get("value") == source_sha
                for f in src.get("facts", [])), "SOURCE_OBSERVATION_DRIFT")
    records = []
    prev = None
    for i, e in enumerate(index["entries"]):
        organ, status = SEQUENCE[i]
        require(e.get("step") == i + 1 and e.get("organ") == organ
                and e.get("status") == status and
                e.get("parents") == ([] if prev is None else [prev]) and
                e.get("verification", {}).get("verified") is True,
                "RELAY_STAGE_DRIFT")
        obj, obj_bytes = load(e.get("id"))
        require(obj.get("schema") == "sia/relay-entry/v0" and obj.get("step") == i + 1
                and obj.get("organ") == organ and obj.get("status") == status
                and obj.get("parents") == e["parents"] and
                obj.get("sourceObservationId") == src_id and
                obj.get("sourceMediaSha256") == source_sha and
                obj.get("evidence") == e.get("evidence") and
                obj.get("verification") == e["verification"] and
                obj.get("permissions") == {
                    "publication": False, "admission": False, "authorityTransferred": False
                }, "VAULT_INDEX_CONTRADICTION")
        if organ == "reLATTE":
            require(obj.get("effect") == "none", "HOLD_IS_NOT_ADMISSION")
        require(len(obj.get("evidence", [])) == len(ROLES[organ]), "EVIDENCE_ROLES_INCOMPLETE")
        roles = {x.get("role") for x in obj["evidence"]}
        require(roles == set(ROLES[organ]) and
                all(x.get("mediaType") == "application/json" and
                    isinstance(x.get("sha256"), str) and
                    len(x["sha256"]) == 71 for x in obj["evidence"]),
                "EVIDENCE_ROLE_OR_DIGEST_INVALID")
        records.append((obj, obj_bytes))
        prev = obj["id"]
    require(len({x[0]["id"] for x in records}) == 5 and
            len(seen | {x[0] for x in SEQUENCE}) == 39,
            "PROJECT_COUNT_CONTRADICTION")
    return index, index_bytes, src, src_bytes, records


def verify_exact_bytes(packet_root, index, records):
    """Optional private local check; no file paths/bytes are exported."""
    root = Path(packet_root).resolve()
    for obj, _ in records:
        for ref in obj["evidence"]:
            path = ROLES[obj["organ"]][ref["role"]]
            raw = read_bounded(root / path, root)
            require(sha(raw) == ref["sha256"], "EVIDENCE_BYTES_CHANGED: " + ref["role"])
    raw = read_bounded(root / "source" / "song.mp3", root, 30 * 1024 * 1024)
    require(sha(raw) == index["sourceMediaSha256"], "ORIGINAL_MEDIA_CHANGED")
    return True


def build_graph(index_path, vault_dir, packet_root=None):
    index, index_raw, observation, observation_raw, records = verify_index_and_vault(index_path, vault_dir)
    exact = verify_exact_bytes(packet_root, index, records) if packet_root else False
    sources, nodes, links = [], [], []
    def source(key, data, ident, schema):
        sid = "source-" + key
        sources.append({
            "id": sid, "source_class": "project-source", "authority": "source-local",
            "locator": {
                "system": "SIA", "container": "local-relay",
                "coordinate": ident, "revision": schema,
                "resolution": "local-content-addressed; external retrieval not asserted"
            },
            "observed_at": observation["capture"]["observedAt"],
            "acquisition": "local-vault-byte-and-id-check",
            "digest": sha(data), "access": "restricted", "export": "pointer-only",
            "redaction": "source metadata and file bytes remain in the owner-local vault"
        })
        return sid
    index_ref = source("index", index_raw, sha(index_raw), index["schema"])
    song_ref = source("song", observation_raw, observation["id"], observation["schema"])
    stage_refs = [source("event" + str(i), raw, obj["id"], obj["schema"])
                  for i, (obj, raw) in enumerate(records, 1)]
    nodes.append({"id": "song", "kind": "artifact", "label": index["title"] + " · source",
                  "status": "observed", "source_ids": [song_ref]})
    def edge(k, frm, to, verb, qualifier, status, citations, authority="none"):
        links.append({"id": k, "from": frm, "to": to, "verb": verb,
                      "qualifier": qualifier, "status": status,
                      "source_ids": citations, "authority": authority})
    for i, ((obj, _), (organ, status)) in enumerate(zip(records, SEQUENCE), 1):
        stage = "stage-" + str(i)
        organ_node = "organ-" + str(i)
        nodes.append({
            "id": stage, "kind": "artifact",
            "label": f"{i:02d} · {organ} · {status}",
            "status": "observed", "source_ids": [stage_refs[i-1], index_ref],
            "extensions": {"sia_object_id": obj["id"], "relay_step": i,
                           "local_effect": obj["effect"],
                           "verification_claim_source": "SIA immutable relay entry"}
        })
        nodes.append({
            "id": organ_node, "kind": "world", "label": organ,
            "status": "observed", "source_ids": [index_ref],
            "extensions": {"membership": "reported by SIA; no owner-currentness claim"}
        })
        edge("source-" + str(i), stage, "song", "connects",
             "SIA reports this event was associated with this song; not a media grant",
             "observed", [stage_refs[i-1], song_ref])
        edge("member-" + str(i), stage, organ_node, "connects",
             "named executing organ according to SIA event record",
             "observed", [stage_refs[i-1]])
        if i > 1:
            edge("parent-" + str(i), stage, "stage-" + str(i-1), "descends-from",
                 "SIA immutable parent event pointer, not a transfer of authority",
                 "observed", [stage_refs[i-1], stage_refs[i-2]])
    for i, p in enumerate(index["proposedRemaining"], 1):
        node = "candidate-" + str(i)
        nodes.append({"id": node, "kind": "question",
                      "label": p["project"] + " · unexecuted invitation",
                      "status": "proposed", "source_ids": [index_ref],
                      "extensions": {"lane": p.get("lane", "unknown"),
                                     "availability": "not checked",
                                     "execution": "not attempted"}})
        edge("invitation-" + str(i), "song", node, "connects",
             "proposal only; no execution, admission, access or consent",
             "proposed", [index_ref])
    packet = {
        "schema": "free-graph.packet/v0",
        "purpose": "RELAY-001: historical SIA five-organ traversal and 34 candidate invitations",
        "modes": ["seed", "re-enter"],
        "scope": {
            "task": "Reveal the bounded RELAY-001 lineage and unexecuted candidate doors",
            "worlds": [n for n, _ in SEQUENCE],
            "resolution": "historical SIA projection, not project currentness"
        },
        "task_world_cut": {
            "status": "sufficient",
            "selected_ids": ["song"] + ["stage-" + str(i) for i in range(1,6)],
            "owner_head_source_ids": [],
            "omitted": [
                {"door": "owner-currentness", "reason": "No owner-selected branch/head was supplied"},
                {"door": "external Suno page", "reason": "Source page authentication not undertaken"},
                {"door": "future organ capability", "reason": "All 34 invitations remain unexecuted"}
            ],
            "rationale": "Locally verified SIA vault is sufficient for a seed/re-entry traversal; not for execution or owner adoption"
        },
        "sources": sources, "nodes": nodes, "links": links,
        "residual_fog": [
            "SIA assertions of upstream verification are historical testimony; Free Graph does not independently replay reLATTE signatures.",
            "Original source media rights, external URL currentness and signer-to-human identity are unestablished.",
            "Project availability and owner-selected current heads are unobserved."
        ],
        "non_imports": [
            "No original audio or local file paths embedded in graph output",
            "No receiver private signing material",
            "No owner-local constitutes link or global truth promotion",
            "Invitation is not an executed project crossing"
        ],
        "extensions": {
            "consumer": "Free Graph native packet projection",
            "source_system": "SIA",
            "mission_id": index["missionId"],
            "source_media_sha256": index["sourceMediaSha256"],
            "sia_index_digest": sha(index_raw),
            "exact_local_evidence_bytes_checked": exact,
            "source_audio_published": False,
            "owner_admission": False,
            "verified_upstream_signatures_here": False,
            "status": "historical-projection"
        },
    }
    out = rehash_packet(packet, stamp=True)
    require(not validate_packet(out), "FREE_GRAPH_VALIDATION_FAILED")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sia-index", type=Path, required=True)
    ap.add_argument("--vault", type=Path, required=True)
    ap.add_argument("--packet-root", type=Path,
                    help="optional exact 5-organ evidence and original audio byte checks")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    try:
        result = build_graph(args.sia_index, args.vault, args.packet_root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"packet_id": packet_id(result), "sources":len(result["sources"]),
            "nodes":len(result["nodes"]), "links":len(result["links"]),
            "source_bytes_checked":result["extensions"]["exact_local_evidence_bytes_checked"],
            "owner_admission":False}, indent=2))
    except (OSError, ValueError, KeyError, TypeError, PacketError) as exc:
        print("Free Graph HOLD: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
