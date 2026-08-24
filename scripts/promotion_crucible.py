#!/usr/bin/env python3
"""Evaluate clause-level invariant translation without trusting shared vocabulary."""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import pathlib
import sys
from typing import Any


CASE_SCHEMA = "promotion-crucible.case/v0"
RECEIPT_SCHEMA = "promotion-crucible.receipt/v0"
CLAUSES = ("epistemic", "authority", "consequence", "historical", "identity")
MATERIALITY_FIELDS = (
    "repository",
    "implementation_family",
    "vocabulary_family",
    "receipt_shape",
)
WARRANT_LEVELS = {"none": 0, "source-local": 1, "owner-local": 2}


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or any(not _nonempty_string(item) for item in value):
        raise ValueError(f"{field} must be a string array")
    if len(set(value)) != len(value):
        raise ValueError(f"{field} must not contain duplicates")
    return value


def _attributable_receipts(value: Any, event_id: str, field: str) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for receipt in value:
        if not isinstance(receipt, dict):
            return False
        receipt_id = receipt.get("id")
        if not _nonempty_string(receipt_id) or receipt_id == event_id:
            return False
        if not _nonempty_string(receipt.get("owner_world")):
            return False
        if not _nonempty_string(receipt.get("decision")):
            return False
    return True


def _trace_result(trace: dict[str, Any], status: str, observations: list[str]) -> dict[str, Any]:
    return {
        "id": trace.get("id"),
        "status": status,
        "observations": observations,
    }


def _evaluate_epistemic(trace: dict[str, Any]) -> dict[str, Any]:
    before_worlds = _string_list(trace.get("compatible_worlds_before"), "compatible_worlds_before")
    after_worlds = _string_list(trace.get("compatible_worlds_after"), "compatible_worlds_after")
    before_sources = _string_list(trace.get("source_ids_before"), "source_ids_before")
    after_sources = _string_list(trace.get("source_ids_after"), "source_ids_after")
    new_sources = sorted(set(after_sources) - set(before_sources))
    world_set_changed = set(before_worlds) != set(after_worlds)
    if world_set_changed and not new_sources:
        return _trace_result(
            trace,
            "refuses",
            ["compatible worlds changed while the underlying source set supplied no new source"],
        )
    if world_set_changed:
        return _trace_result(
            trace,
            "satisfies",
            ["compatible worlds changed only alongside separately attributable new source IDs: " + ", ".join(new_sources)],
        )
    return _trace_result(
        trace,
        "satisfies",
        ["compatible worlds remained unchanged under re-expression"],
    )


def _evaluate_authority(trace: dict[str, Any]) -> dict[str, Any]:
    before = trace.get("effective_warrant_before")
    after = trace.get("effective_warrant_after")
    if before not in WARRANT_LEVELS or after not in WARRANT_LEVELS:
        raise ValueError("effective warrant must be none, source-local, or owner-local")
    event_id = trace.get("projection_event_id")
    if not _nonempty_string(event_id):
        raise ValueError("authority trace needs projection_event_id")
    warrant_rose = WARRANT_LEVELS[after] > WARRANT_LEVELS[before]
    permission_rose = trace.get("action_unlocked") is True
    if warrant_rose or permission_rose:
        if not _attributable_receipts(trace.get("gate_receipts"), event_id, "gate_receipts"):
            return _trace_result(
                trace,
                "refuses",
                ["effective warrant or permission rose without a separately attributable local gate"],
            )
        return _trace_result(
            trace,
            "satisfies",
            ["effective warrant or permission rose only through a separately attributable local gate"],
        )
    return _trace_result(
        trace,
        "satisfies",
        ["projection left effective warrant and permission unchanged"],
    )


def _evaluate_consequence(trace: dict[str, Any]) -> dict[str, Any]:
    event_id = trace.get("projection_event_id")
    if not _nonempty_string(event_id):
        raise ValueError("consequence trace needs projection_event_id")
    before = trace.get("state_before")
    after = trace.get("state_after")
    if not _nonempty_string(before) or not _nonempty_string(after):
        raise ValueError("consequence trace needs non-empty state_before and state_after")
    if before != after:
        if not _attributable_receipts(trace.get("gate_receipts"), event_id, "gate_receipts"):
            return _trace_result(
                trace,
                "refuses",
                ["consequential state changed without a separately attributable local gate"],
            )
        return _trace_result(
            trace,
            "satisfies",
            ["projection participated in a causal path whose state change is attributed to a separate local gate"],
        )
    return _trace_result(
        trace,
        "satisfies",
        ["projection did not itself constitute a consequential state change"],
    )


def _projection_map(value: Any, field: str) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for projection in value:
        if not isinstance(projection, dict) or not _nonempty_string(projection.get("id")):
            raise ValueError(f"{field} entries need a non-empty id")
        if projection["id"] in result:
            raise ValueError(f"{field} projection ids must be unique")
        result[projection["id"]] = projection
    return result


def _evaluate_historical(trace: dict[str, Any]) -> dict[str, Any]:
    before = _projection_map(trace.get("prior_projections_before"), "prior_projections_before")
    after = _projection_map(trace.get("prior_projections_after"), "prior_projections_after")
    new = _projection_map(trace.get("new_projections"), "new_projections")
    observations: list[str] = []
    for projection_id, original in before.items():
        if projection_id not in after:
            return _trace_result(trace, "refuses", [f"prior projection {projection_id} disappeared"])
        if after[projection_id] != original:
            return _trace_result(trace, "refuses", [f"prior projection {projection_id} was rewritten"])
    if set(before) != set(after):
        return _trace_result(
            trace,
            "refuses",
            ["prior_projections_after must preserve exactly the previously attributable projections"],
        )
    if set(before) & set(new):
        return _trace_result(trace, "refuses", ["new decoder output reused a prior projection id"])
    if trace.get("decoder_changed") is True:
        if not new:
            return _trace_result(trace, "refuses", ["decoder changed without appending a new projection"])
        for projection_id, projection in new.items():
            if not _nonempty_string(projection.get("decoder_version")):
                return _trace_result(trace, "refuses", [f"new projection {projection_id} lacks decoder attribution"])
            derived = projection.get("derived_from_projection_ids")
            if not isinstance(derived, list) or not derived or any(item not in before for item in derived):
                return _trace_result(trace, "refuses", [f"new projection {projection_id} lacks valid derivation attribution"])
        observations.append("decoder change appended newly identified and attributed projection output")
    elif new:
        return _trace_result(trace, "refuses", ["new projection appeared without a declared decoder change"])
    observations.append("all prior projection identifiers and content remained byte-stable")
    return _trace_result(trace, "satisfies", observations)


def _evaluate_identity(trace: dict[str, Any]) -> dict[str, Any]:
    operation = trace.get("operation_kind")
    if operation not in {"view", "object-transform"}:
        raise ValueError("operation_kind must be view or object-transform")
    event_id = trace.get("projection_event_id")
    if not _nonempty_string(event_id):
        raise ValueError("identity trace needs projection_event_id")
    identity_fields = (
        "object_id_before",
        "object_id_after",
        "worldline_id_before",
        "worldline_id_after",
    )
    if any(not _nonempty_string(trace.get(field)) for field in identity_fields):
        raise ValueError("identity trace needs object and worldline ids before and after")
    changed = (
        trace["object_id_before"] != trace["object_id_after"]
        or trace["worldline_id_before"] != trace["worldline_id_after"]
    )
    if operation == "view" and changed:
        return _trace_result(trace, "refuses", ["view operation silently changed object or worldline identity"])
    if operation == "object-transform" and changed:
        if not _attributable_receipts(trace.get("transform_receipts"), event_id, "transform_receipts"):
            return _trace_result(trace, "refuses", ["object identity changed without a separately attributable transform receipt"])
        return _trace_result(trace, "satisfies", ["identity change is attributed to an explicit object transform"])
    return _trace_result(trace, "satisfies", ["view or no-op preserved object and worldline identity"])


TRACE_EVALUATORS = {
    "epistemic": _evaluate_epistemic,
    "authority": _evaluate_authority,
    "consequence": _evaluate_consequence,
    "historical": _evaluate_historical,
    "identity": _evaluate_identity,
}


def evaluate_trace(clause: str, trace: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one normalized operational trace for a named candidate clause."""
    if clause not in TRACE_EVALUATORS:
        raise ValueError(f"unknown clause {clause!r}")
    if not isinstance(trace, dict) or not _nonempty_string(trace.get("id")):
        raise ValueError("trace must be an object with a non-empty id")
    return TRACE_EVALUATORS[clause](trace)


def _adapt_ssw_math_001(receipt: dict[str, Any], clauses: list[str]) -> dict[str, list[dict[str, Any]]]:
    if receipt.get("receipt_schema") != "ssw-math.receipt/v0":
        raise ValueError("SSW adapter requires ssw-math.receipt/v0")
    requested = _string_list(clauses, "native_receipt.clauses")
    if any(clause not in {"epistemic", "identity"} for clause in requested):
        raise ValueError("SSW-MATH-001 adapter only exposes epistemic and identity clauses")
    world_ids = sorted(receipt.get("world_results", {}))
    reexpressions = receipt.get("reexpression_results")
    if not isinstance(reexpressions, list):
        raise ValueError("SSW receipt reexpression_results must be an array")
    adapted: dict[str, list[dict[str, Any]]] = {}
    if "epistemic" in requested:
        passed = (
            receipt.get("observation_collision") is True
            and len(world_ids) >= 2
            and bool(reexpressions)
            and all(item.get("outputs_equal") is True for item in reexpressions if isinstance(item, dict))
            and all(isinstance(item, dict) for item in reexpressions)
        )
        adapted["epistemic"] = [{
            "id": "native:ssw-math-001:observation-collision",
            "status": "satisfies" if passed else "refuses",
            "observations": [
                "native observation collision and deterministic re-expressions preserve the same candidate graph worlds"
                if passed else
                "native receipt did not preserve its compatible graph worlds under re-expression"
            ],
        }]
    if "identity" in requested:
        passed = (
            receipt.get("observation_collision") is True
            and receipt.get("isomorphic") is False
            and len(world_ids) >= 2
        )
        adapted["identity"] = [{
            "id": "native:ssw-math-001:distinct-graph-worlds",
            "status": "satisfies" if passed else "refuses",
            "observations": [
                "native receipt preserves two non-isomorphic graph identities despite their equal supplied observation"
                if passed else
                "native receipt did not preserve distinct world identities across the observation collision"
            ],
        }]
    return adapted


def _adapt_copied_projection_poison(
    receipt: dict[str, Any],
    clauses: list[str],
) -> dict[str, list[dict[str, Any]]]:
    if receipt.get("receiptSchema") != "free-graph.relational-coordinate.receipt/v0":
        raise ValueError("copied projection poison adapter requires the copied receipt silhouette")
    requested = _string_list(clauses, "native_receipt.clauses")
    if any(clause not in {"authority", "consequence"} for clause in requested):
        raise ValueError("copied projection poison adapter only exposes authority and consequence")
    projection = receipt.get("projection")
    trace = receipt.get("operationalTrace")
    if not isinstance(projection, dict) or not _nonempty_string(projection.get("id")):
        raise ValueError("copied projection poison receipt needs projection.id")
    if not isinstance(trace, dict):
        raise ValueError("copied projection poison receipt needs operationalTrace")
    adapted: dict[str, list[dict[str, Any]]] = {}
    if "authority" in requested:
        normalized = {
            "id": "native:poison:authority",
            "projection_event_id": projection["id"],
            "effective_warrant_before": trace.get("effectiveWarrantBefore"),
            "effective_warrant_after": trace.get("effectiveWarrantAfter"),
            "action_unlocked": trace.get("actionUnlocked"),
            "gate_receipts": trace.get("gateReceipts"),
        }
        adapted["authority"] = [evaluate_trace("authority", normalized)]
    if "consequence" in requested:
        normalized = {
            "id": "native:poison:consequence",
            "projection_event_id": projection["id"],
            "state_before": trace.get("stateBefore"),
            "state_after": trace.get("stateAfter"),
            "gate_receipts": trace.get("gateReceipts"),
        }
        adapted["consequence"] = [evaluate_trace("consequence", normalized)]
    return adapted


NATIVE_ADAPTERS = {
    "ssw-math-001/v0": _adapt_ssw_math_001,
    "copied-projection-poison/v0": _adapt_copied_projection_poison,
}


def _validate_case(case: dict[str, Any]) -> None:
    if not isinstance(case, dict) or case.get("case_schema") != CASE_SCHEMA:
        raise ValueError(f"case_schema must equal {CASE_SCHEMA!r}")
    if not _nonempty_string(case.get("candidate_id")):
        raise ValueError("candidate_id must be non-empty")
    clauses = case.get("clauses")
    if not isinstance(clauses, dict) or set(clauses) != set(CLAUSES):
        raise ValueError("case must define exactly the five crucible clauses")
    for name in CLAUSES:
        specification = clauses[name]
        if not isinstance(specification, dict):
            raise ValueError(f"clause {name} must be an object")
        for field in ("statement", "semantic_fracture", "missing_discriminator"):
            if not _nonempty_string(specification.get(field)):
                raise ValueError(f"clause {name}.{field} must be non-empty")
    consumers = case.get("consumers")
    if not isinstance(consumers, list) or not consumers:
        raise ValueError("consumers must be a non-empty array")
    ids: set[str] = set()
    for consumer in consumers:
        if not isinstance(consumer, dict) or not _nonempty_string(consumer.get("id")):
            raise ValueError("each consumer needs a non-empty id")
        if consumer["id"] in ids:
            raise ValueError("consumer ids must be unique")
        ids.add(consumer["id"])
        if consumer.get("role") not in {"embodiment", "poison"}:
            raise ValueError(f"consumer {consumer['id']} role must be embodiment or poison")
        materiality = consumer.get("materiality")
        if not isinstance(materiality, dict):
            raise ValueError(f"consumer {consumer['id']} needs materiality")
        for field in MATERIALITY_FIELDS:
            if not _nonempty_string(materiality.get(field)):
                raise ValueError(f"consumer {consumer['id']} materiality.{field} must be non-empty")
        traces = consumer.get("traces", {})
        if not isinstance(traces, dict) or any(name not in CLAUSES for name in traces):
            raise ValueError(f"consumer {consumer['id']} traces contain an unknown clause")
        if consumer.get("role") == "poison":
            attack = consumer.get("mandatory_attack")
            if not isinstance(attack, dict):
                raise ValueError(f"poison {consumer['id']} needs mandatory_attack")
            required = _string_list(attack.get("must_refuse"), "mandatory_attack.must_refuse")
            if any(name not in CLAUSES for name in required):
                raise ValueError(f"poison {consumer['id']} requires an unknown clause")


def _load_native_results(consumer: dict[str, Any], base_dir: pathlib.Path) -> dict[str, list[dict[str, Any]]]:
    specification = consumer.get("native_receipt")
    if specification is None:
        return {}
    if not isinstance(specification, dict):
        raise ValueError(f"consumer {consumer['id']} native_receipt must be an object")
    relative_path = specification.get("path")
    expected_digest = specification.get("sha256")
    adapter_name = specification.get("adapter")
    if not _nonempty_string(relative_path) or not _nonempty_string(expected_digest):
        raise ValueError(f"consumer {consumer['id']} native_receipt path and sha256 are required")
    if adapter_name not in NATIVE_ADAPTERS:
        raise ValueError(f"unknown native receipt adapter {adapter_name!r}")
    receipt_path = base_dir / relative_path
    try:
        receipt_bytes = receipt_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read native receipt {receipt_path}: {exc}") from exc
    observed_digest = _sha256_bytes(receipt_bytes)
    if observed_digest != expected_digest:
        raise ValueError(
            f"native receipt digest mismatch for {consumer['id']}: expected {expected_digest}, got {observed_digest}"
        )
    try:
        receipt = json.loads(receipt_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"native receipt for {consumer['id']} is not valid JSON") from exc
    return NATIVE_ADAPTERS[adapter_name](receipt, specification.get("clauses"))


def _evaluate_consumer(consumer: dict[str, Any], base_dir: pathlib.Path) -> dict[str, Any]:
    details: dict[str, list[dict[str, Any]]] = {name: [] for name in CLAUSES}
    for clause, traces in consumer.get("traces", {}).items():
        if not isinstance(traces, list):
            raise ValueError(f"consumer {consumer['id']} traces.{clause} must be an array")
        details[clause].extend(evaluate_trace(clause, trace) for trace in traces)
    for clause, results in _load_native_results(consumer, base_dir).items():
        details[clause].extend(results)

    clause_results: dict[str, dict[str, Any]] = {}
    for clause in CLAUSES:
        results = details[clause]
        if not results:
            status = "not-tested"
        elif any(result["status"] == "refuses" for result in results):
            status = "refuses"
        else:
            status = "satisfies"
        clause_results[clause] = {
            "status": status,
            "trace_count": len(results),
            "traces": results,
        }
    return {
        "id": consumer["id"],
        "role": consumer["role"],
        "source": copy.deepcopy(consumer.get("source")),
        "materiality": copy.deepcopy(consumer["materiality"]),
        "declared_policy": copy.deepcopy(consumer.get("declared_policy")),
        "declared_policy_consulted": False,
        "clauses": clause_results,
    }


def _materially_independent(combo: tuple[dict[str, Any], ...]) -> bool:
    for field in MATERIALITY_FIELDS:
        values = {item["materiality"][field] for item in combo}
        if len(values) != len(combo):
            return False
    return True


def _maximum_independent_supports(supporters: list[dict[str, Any]]) -> list[str]:
    ordered = sorted(supporters, key=lambda item: item["id"])
    for size in range(len(ordered), 0, -1):
        for combo in itertools.combinations(ordered, size):
            if _materially_independent(combo):
                return [item["id"] for item in combo]
    return []


def _clause_verdict(
    name: str,
    specification: dict[str, Any],
    consumer_results: list[dict[str, Any]],
) -> dict[str, Any]:
    embodiments = [item for item in consumer_results if item["role"] == "embodiment"]
    supporters = [item for item in embodiments if item["clauses"][name]["status"] == "satisfies"]
    refusers = [item for item in embodiments if item["clauses"][name]["status"] == "refuses"]
    independent = _maximum_independent_supports(supporters)
    if refusers:
        verdict = "refuses"
    elif len(independent) >= 2:
        verdict = "supports"
    elif len(independent) == 1:
        verdict = "only-one-domain"
    else:
        verdict = "unresolved"
    nonindependent = sorted(item["id"] for item in supporters if item["id"] not in independent)
    return {
        "statement": specification["statement"],
        "verdict": verdict,
        "independent_supports": independent,
        "nonindependent_supports": nonindependent,
        "refusing_embodiments": sorted(item["id"] for item in refusers),
        "semantic_fracture": specification["semantic_fracture"] if verdict != "supports" else None,
        "missing_discriminator": specification["missing_discriminator"] if verdict != "supports" else None,
    }


def _attack_results(case: dict[str, Any], consumer_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in consumer_results}
    attacks = []
    for consumer in case["consumers"]:
        if consumer["role"] != "poison":
            continue
        required = sorted(consumer["mandatory_attack"]["must_refuse"])
        result = by_id[consumer["id"]]
        observed = sorted(
            clause for clause in CLAUSES
            if result["clauses"][clause]["status"] == "refuses"
        )
        missing = sorted(set(required) - set(observed))
        attacks.append({
            "consumer_id": consumer["id"],
            "copied_vocabulary_family": consumer["materiality"]["vocabulary_family"],
            "copied_receipt_shape": consumer["materiality"]["receipt_shape"],
            "declared_policy_consulted": False,
            "required_refusals": required,
            "observed_refusals": observed,
            "missing_refusals": missing,
            "outcome": "caught" if not missing else "vocabulary-leak-detected",
        })
    return attacks


def evaluate_case(case: dict[str, Any], base_dir: str | pathlib.Path = ".") -> dict[str, Any]:
    """Evaluate a complete promotion crucible case and return a deterministic receipt value."""
    _validate_case(case)
    base_path = pathlib.Path(base_dir)
    consumer_results = [_evaluate_consumer(consumer, base_path) for consumer in case["consumers"]]
    clauses = {
        name: _clause_verdict(name, case["clauses"][name], consumer_results)
        for name in CLAUSES
    }
    attacks = _attack_results(case, consumer_results)
    attacks_caught = bool(attacks) and all(attack["outcome"] == "caught" for attack in attacks)
    all_clauses_support = all(result["verdict"] == "supports" for result in clauses.values())
    if not attacks_caught:
        whole_verdict = "crucible-refused"
        whole_reason = "a mandatory vocabulary-leak poison was not refused on every required behavior"
    elif all_clauses_support:
        whole_verdict = "portable-candidate"
        whole_reason = "every clause independently survived translation and every mandatory poison was caught"
    else:
        whole_verdict = "split-required"
        whole_reason = "the candidate conjunction contains clauses that have not independently survived translation"

    source_pins = []
    for consumer in case["consumers"]:
        source = consumer.get("source", {})
        pin = {
            "consumer_id": consumer["id"],
            "repository": source.get("repository"),
            "revision": source.get("revision"),
            "path": source.get("path"),
        }
        if "native_receipt" in consumer:
            pin["native_receipt_sha256"] = consumer["native_receipt"]["sha256"]
        source_pins.append(pin)

    return {
        "receipt_schema": RECEIPT_SCHEMA,
        "candidate_id": case["candidate_id"],
        "case_digest": "sha256:" + _sha256_bytes(_canonical_bytes(case)),
        "promotion_rule": case.get("promotion_rule"),
        "candidate_law_is_conjunction": True,
        "aggregate_score": None,
        "aggregation_policy": "forbidden; clause verdicts are not averaged",
        "source_pins": source_pins,
        "consumer_results": consumer_results,
        "attacks": attacks,
        "clauses": clauses,
        "whole": {
            "verdict": whole_verdict,
            "reason": whole_reason,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    case_path = pathlib.Path(args.case)
    try:
        case = json.loads(case_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read case {case_path}: {exc}")
    receipt = evaluate_case(case, case_path.parent)
    rendered = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
