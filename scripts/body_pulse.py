#!/usr/bin/env python3
"""BODY-PULSE-001: derive occurrence-bound charts and compose a no-promotion body projection."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("body_overlap", HERE / "body_overlap.py")
body_overlap = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(body_overlap)

SURFACE_SCHEMA = "body.surface/v0"
SNAPSHOT_SCHEMA = "body.snapshot/v0"
PULSE_SCHEMA = "body.pulse-receipt/v0"
OWNER_INTERFACE_WITNESS_SCHEMA = "body.owner-interface-witness/v0"
SURFACE_DRIFT_SCHEMA = "body.surface-drift-receipt/v0"


class BodyPulseError(ValueError):
    pass


def _canonical_bytes(value: Any, omit_key: str | None = None) -> bytes:
    value = copy.deepcopy(value)
    if omit_key and isinstance(value, dict):
        value.pop(omit_key, None)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _digest(prefix: str, value: Any, omit_key: str | None = None) -> str:
    return f"{prefix}:sha256:{hashlib.sha256(_canonical_bytes(value, omit_key)).hexdigest()}"


def pulse_id(receipt: dict[str, Any]) -> str:
    return _digest("bodypulse", receipt, "pulse_id")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_surface(surface: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if surface.get("schema") != SURFACE_SCHEMA:
        errors.append(f"$.schema must equal {SURFACE_SCHEMA!r}")
    if not _nonempty(surface.get("organ")):
        errors.append("$.organ must be non-empty")
    if not _nonempty(surface.get("owner")):
        errors.append("$.owner must be non-empty")
    if surface.get("authority") != "none":
        errors.append("$.authority must equal 'none' for BODY-PULSE-001")

    chart = {
        "schema": body_overlap.CHART_SCHEMA,
        "owner": {"world": surface.get("owner"), "occurrence": "surface-validation"},
        "provides": surface.get("provides"),
        "needs": surface.get("needs"),
        "interfaces": surface.get("interfaces"),
        "measure": surface.get("measure"),
        "receipts": surface.get("receipts"),
        "residual_fog": surface.get("residual_fog"),
        "non_authorities": surface.get("non_authorities"),
    }
    errors.extend("surface: " + error for error in body_overlap.validate_chart(chart))

    evidence = surface.get("evidence", [])
    if not isinstance(evidence, list):
        errors.append("$.evidence must be an array")
    return errors


def derive_chart(surface: dict[str, Any], occurrence: str) -> dict[str, Any]:
    errors = validate_surface(surface)
    if errors:
        raise BodyPulseError("invalid body surface:\n" + "\n".join("- " + e for e in errors))
    if not _nonempty(occurrence):
        raise BodyPulseError("occurrence must be non-empty")

    chart = {
        "schema": body_overlap.CHART_SCHEMA,
        "owner": {
            "world": surface["owner"],
            "occurrence": occurrence,
        },
        "provides": copy.deepcopy(surface["provides"]),
        "needs": copy.deepcopy(surface["needs"]),
        "interfaces": copy.deepcopy(surface["interfaces"]),
        "measure": copy.deepcopy(surface["measure"]),
        "receipts": copy.deepcopy(surface["receipts"]),
        "residual_fog": copy.deepcopy(surface["residual_fog"]),
        "non_authorities": copy.deepcopy(surface["non_authorities"]),
    }
    chart["chart_id"] = body_overlap.chart_id(chart)
    return chart


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BodyPulseError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BodyPulseError(f"JSON root must be an object: {path}")
    return value


def load_snapshot(path: str | Path) -> tuple[dict[str, Any], Path]:
    snapshot_path = Path(path)
    snapshot = _load_json(snapshot_path)
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise BodyPulseError(f"$.schema must equal {SNAPSHOT_SCHEMA!r}")
    entries = snapshot.get("organs")
    if not isinstance(entries, list) or not entries:
        raise BodyPulseError("$.organs must be a non-empty array")
    return snapshot, snapshot_path.parent


def derive_snapshot_charts(
    snapshot: dict[str, Any],
    base_dir: Path,
    *,
    surface_drift_receipts: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    charts: list[dict[str, Any]] = []
    seen_owners: set[str] = set()

    for index, entry in enumerate(snapshot["organs"]):
        if not isinstance(entry, dict):
            raise BodyPulseError(f"$.organs[{index}] must be an object")
        for field in ("surface_path", "surface_digest", "occurrence"):
            if not _nonempty(entry.get(field)):
                raise BodyPulseError(f"$.organs[{index}].{field} must be non-empty")

        surface_path = (base_dir / entry["surface_path"]).resolve()
        surface = _load_json(surface_path)
        actual_digest = _sha256(surface)
        if actual_digest != entry["surface_digest"]:
            raise BodyPulseError(
                f"$.organs[{index}] surface digest mismatch: "
                f"expected {entry['surface_digest']}, got {actual_digest}"
            )

        chart = derive_chart(surface, entry["occurrence"])
        owner = chart["owner"]["world"]
        if owner in seen_owners:
            raise BodyPulseError(f"duplicate owner in snapshot: {owner}")
        seen_owners.add(owner)
        charts.append(chart)

        witness_path_value = entry.get("owner_witness_path")
        witness_digest_value = entry.get("owner_witness_digest")
        if bool(witness_path_value) != bool(witness_digest_value):
            raise BodyPulseError(
                f"$.organs[{index}] owner_witness_path and owner_witness_digest must appear together"
            )
        if witness_path_value:
            witness_path = (base_dir / str(witness_path_value)).resolve()
            witness = _load_json(witness_path)
            actual_witness_digest = _sha256(witness)
            if actual_witness_digest != witness_digest_value:
                raise BodyPulseError(
                    f"$.organs[{index}] owner witness digest mismatch: "
                    f"expected {witness_digest_value}, got {actual_witness_digest}"
                )
            drift = detect_surface_drift(surface, witness, entry["occurrence"])
            if surface_drift_receipts is not None:
                surface_drift_receipts.append(drift)

    return sorted(charts, key=lambda c: (c["owner"]["world"], c["owner"]["occurrence"]))


def _declaration_key(value: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(value.get("kind", "")),
        str(value.get("protocol", "")),
        str(value.get("version", "")),
    )


def _interface_key(value: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(value.get("direction", "")),
        str(value.get("kind", "")),
        str(value.get("protocol", "")),
        str(value.get("version", "")),
    )


def validate_owner_interface_witness(witness: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if witness.get("schema") != OWNER_INTERFACE_WITNESS_SCHEMA:
        errors.append(f"$.schema must equal {OWNER_INTERFACE_WITNESS_SCHEMA!r}")
    if not _nonempty(witness.get("owner")):
        errors.append("$.owner must be non-empty")
    if not _nonempty(witness.get("occurrence")):
        errors.append("$.occurrence must be non-empty")
    for field in ("provides", "interfaces", "evidence"):
        if not isinstance(witness.get(field), list):
            errors.append(f"$.{field} must be an array")

    for index, record in enumerate(witness.get("provides", [])):
        if not isinstance(record, dict):
            errors.append(f"$.provides[{index}] must be an object")
            continue
        for field in ("kind", "protocol", "version"):
            if not _nonempty(record.get(field)):
                errors.append(f"$.provides[{index}].{field} must be non-empty")

    for index, record in enumerate(witness.get("interfaces", [])):
        if not isinstance(record, dict):
            errors.append(f"$.interfaces[{index}] must be an object")
            continue
        if not _nonempty(record.get("name")):
            errors.append(f"$.interfaces[{index}].name must be non-empty")
        if record.get("direction") not in body_overlap.DIRECTIONS:
            errors.append(f"$.interfaces[{index}].direction must be 'emit' or 'accept'")
        for field in ("kind", "protocol", "version"):
            if not _nonempty(record.get(field)):
                errors.append(f"$.interfaces[{index}].{field} must be non-empty")
    return errors


def detect_surface_drift(
    surface: dict[str, Any],
    witness: dict[str, Any],
    occurrence: str,
) -> dict[str, Any]:
    surface_errors = validate_surface(surface)
    if surface_errors:
        raise BodyPulseError("invalid body surface:\n" + "\n".join("- " + e for e in surface_errors))
    witness_errors = validate_owner_interface_witness(witness)
    if witness_errors:
        raise BodyPulseError("invalid owner interface witness:\n" + "\n".join("- " + e for e in witness_errors))
    if witness["owner"] != surface["owner"]:
        raise BodyPulseError("owner interface witness does not belong to surface owner")
    if witness["occurrence"] != occurrence:
        raise BodyPulseError("owner interface witness occurrence does not match snapshot occurrence")

    declared_provides = {_declaration_key(item) for item in surface["provides"]}
    declared_interfaces = {_interface_key(item) for item in surface["interfaces"]}
    missing_provides = [
        copy.deepcopy(item)
        for item in witness["provides"]
        if _declaration_key(item) not in declared_provides
    ]
    missing_interfaces = [
        copy.deepcopy(item)
        for item in witness["interfaces"]
        if _interface_key(item) not in declared_interfaces
    ]

    receipt: dict[str, Any] = {
        "schema": SURFACE_DRIFT_SCHEMA,
        "world": surface["owner"],
        "occurrence": occurrence,
        "status": "drift" if missing_provides or missing_interfaces else "aligned",
        "surface_digest": _sha256(surface),
        "owner_witness_digest": _sha256(witness),
        "missing_provides": _sorted_unique(missing_provides),
        "missing_interfaces": _sorted_unique(missing_interfaces),
        "evidence": copy.deepcopy(witness["evidence"]),
        "authority": "none",
        "non_promotions": [
            "owner witness != body declaration",
            "surface drift != auto-repair",
            "surface drift != authority transfer",
            "absence from surface != absence from owner reality",
        ],
    }
    receipt["drift_id"] = _digest("bodydrift", receipt, "drift_id")
    return receipt


def _edge_key(value: dict[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(value.get("from_world", "")),
        str(value.get("to_world", "")),
        str(value.get("kind", "")),
        str(value.get("protocol", value.get("emitted", ""))),
        str(value.get("version", value.get("accepted", ""))),
    )


def _sorted_unique(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[bytes, dict[str, Any]] = {}
    for record in records:
        unique[_canonical_bytes(record)] = record
    return [unique[key] for key in sorted(unique)]


def compose_pulse(charts: list[dict[str, Any]], *, label: str | None = None) -> dict[str, Any]:
    if not charts:
        raise BodyPulseError("at least one chart is required")

    pairwise: list[dict[str, Any]] = []
    exact_edges: list[dict[str, Any]] = []
    adapter_edges: list[dict[str, Any]] = []

    for left_index in range(len(charts)):
        for right_index in range(left_index + 1, len(charts)):
            receipt = body_overlap.compare_charts(charts[left_index], charts[right_index])
            pairwise.append(receipt)
            exact_edges.extend(receipt["exact_interfaces"])
            exact_edges.extend(receipt["need_offer_matches"])
            adapter_edges.extend(receipt["adapter_candidates"])

    exact_edges = _sorted_unique(exact_edges)
    adapter_edges = _sorted_unique(adapter_edges)

    unmet_needs: list[dict[str, Any]] = []
    for chart in charts:
        neighbor_provided_keys = {
            _declaration_key(item)
            for provider in charts
            if provider["owner"]["world"] != chart["owner"]["world"]
            for item in provider.get("provides", [])
        }
        for need in chart.get("needs", []):
            if _declaration_key(need) not in neighbor_provided_keys:
                unmet_needs.append({
                    "world": chart["owner"]["world"],
                    "occurrence": chart["owner"]["occurrence"],
                    "kind": need["kind"],
                    "protocol": need["protocol"],
                    "version": need["version"],
                })

    touched: set[str] = set()
    for edge in exact_edges + adapter_edges:
        touched.add(str(edge.get("from_world", "")))
        touched.add(str(edge.get("to_world", "")))
    isolated = [
        {
            "world": chart["owner"]["world"],
            "occurrence": chart["owner"]["occurrence"],
        }
        for chart in charts
        if chart["owner"]["world"] not in touched
    ]

    receipt: dict[str, Any] = {
        "schema": PULSE_SCHEMA,
        "label": label,
        "charts": [
            {
                "chart_id": chart["chart_id"],
                "world": chart["owner"]["world"],
                "occurrence": chart["owner"]["occurrence"],
            }
            for chart in charts
        ],
        "pairwise_receipts": [
            {
                "receipt_id": receipt["receipt_id"],
                "left_world": receipt["left_chart"]["world"],
                "right_world": receipt["right_chart"]["world"],
            }
            for receipt in pairwise
        ],
        "exact_edges": exact_edges,
        "adapter_edges": adapter_edges,
        "unmet_needs": _sorted_unique(unmet_needs),
        "isolated_charts": isolated,
        "counts": {
            "charts": len(charts),
            "pairwise_comparisons": len(pairwise),
            "exact_edges": len(exact_edges),
            "adapter_edges": len(adapter_edges),
            "unmet_needs": len(_sorted_unique(unmet_needs)),
            "isolated_charts": len(isolated),
        },
        "authority": "none",
        "non_promotions": [
            "pulse != body authority",
            "edge count != worth",
            "centrality != canon",
            "unmet need != command",
            "candidate overlap != admitted join",
            "absence from pulse != nonexistence",
        ],
    }
    receipt["pulse_id"] = pulse_id(receipt)
    return receipt


def run_snapshot(path: str | Path) -> dict[str, Any]:
    snapshot, base_dir = load_snapshot(path)
    surface_drift_receipts: list[dict[str, Any]] = []
    charts = derive_snapshot_charts(
        snapshot,
        base_dir,
        surface_drift_receipts=surface_drift_receipts,
    )
    receipt = compose_pulse(charts, label=snapshot.get("label"))
    if surface_drift_receipts:
        receipt["surface_drift_receipts"] = _sorted_unique(surface_drift_receipts)
        receipt["counts"]["surface_drifts"] = sum(
            1 for item in surface_drift_receipts if item["status"] == "drift"
        )
        receipt["non_promotions"].append("surface drift != auto-repair")
        receipt["pulse_id"] = pulse_id(receipt)
    return receipt


def _dump(value: Any, path: str | None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("snapshot")
    root.add_argument("--output")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        receipt = run_snapshot(args.snapshot)
    except BodyPulseError as exc:
        sys.stderr.write(f"error:\n{exc}\n")
        return 1
    _dump(receipt, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
