#!/usr/bin/env python3
"""BODY-OVERLAP-001: deterministic comparison of two occurrence-bound body charts."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

CHART_SCHEMA = "body.chart/v0"
RECEIPT_SCHEMA = "body.overlap-receipt/v0"
DIRECTIONS = {"emit", "accept"}


class BodyOverlapError(ValueError):
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


def _digest(prefix: str, value: Any, omit_key: str | None = None) -> str:
    return f"{prefix}:sha256:{hashlib.sha256(_canonical_bytes(value, omit_key)).hexdigest()}"


def chart_id(chart: dict[str, Any]) -> str:
    return _digest("bodyc", chart, "chart_id")


def receipt_id(receipt: dict[str, Any]) -> str:
    return _digest("bodyov", receipt, "receipt_id")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _decl_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(record.get("kind", "")),
        str(record.get("protocol", "")),
        str(record.get("version", "")),
    )


def _repr_key(record: dict[str, Any]) -> tuple[str, str]:
    return (
        str(record.get("protocol", "")),
        str(record.get("version", "")),
    )


def validate_chart(chart: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if chart.get("schema") != CHART_SCHEMA:
        errors.append(f"$.schema must equal {CHART_SCHEMA!r}")

    owner = chart.get("owner")
    if not isinstance(owner, dict):
        errors.append("$.owner must be an object")
    else:
        if not _nonempty(owner.get("world")):
            errors.append("$.owner.world must be non-empty")
        if not _nonempty(owner.get("occurrence")):
            errors.append("$.owner.occurrence must be non-empty")

    for field in ("provides", "needs", "interfaces", "receipts", "residual_fog", "non_authorities"):
        if not isinstance(chart.get(field), list):
            errors.append(f"$.{field} must be an array")

    measure = chart.get("measure")
    if not isinstance(measure, dict):
        errors.append("$.measure must be an object")
    else:
        for field in ("declared", "observed"):
            if not isinstance(measure.get(field), list):
                errors.append(f"$.measure.{field} must be an array")

    for field in ("provides", "needs"):
        records = chart.get(field, [])
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            path = f"$.{field}[{index}]"
            if not isinstance(record, dict):
                errors.append(path + " must be an object")
                continue
            if not _nonempty(record.get("kind")):
                errors.append(path + ".kind must be non-empty")
            if not _nonempty(record.get("protocol")):
                errors.append(path + ".protocol must be non-empty")
            if not _nonempty(record.get("version")):
                errors.append(path + ".version must be non-empty")

    interfaces = chart.get("interfaces", [])
    if isinstance(interfaces, list):
        for index, record in enumerate(interfaces):
            path = f"$.interfaces[{index}]"
            if not isinstance(record, dict):
                errors.append(path + " must be an object")
                continue
            if record.get("direction") not in DIRECTIONS:
                errors.append(path + ".direction must be 'emit' or 'accept'")
            for field in ("kind", "protocol", "version"):
                if not _nonempty(record.get(field)):
                    errors.append(path + f".{field} must be non-empty")

    supplied = chart.get("chart_id")
    if supplied is not None and supplied != chart_id(chart):
        errors.append("$.chart_id does not match chart content")

    return errors


def load_chart(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BodyOverlapError(f"cannot read body chart {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise BodyOverlapError(f"body chart {path} root must be an object")
    errors = validate_chart(value)
    if errors:
        raise BodyOverlapError("\n".join("- " + error for error in errors))
    return value


def _match_declarations(
    source: dict[str, Any],
    destination: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    exact: list[dict[str, Any]] = []
    adapters: list[dict[str, Any]] = []

    for provided in source.get("provides", []):
        for need in destination.get("needs", []):
            if provided.get("kind") != need.get("kind"):
                continue
            item = {
                "from_world": source["owner"]["world"],
                "to_world": destination["owner"]["world"],
                "kind": provided["kind"],
                "provided": _repr_key(provided),
                "needed": _repr_key(need),
            }
            if _decl_key(provided) == _decl_key(need):
                item["protocol"] = provided["protocol"]
                item["version"] = provided["version"]
                item.pop("provided")
                item.pop("needed")
                exact.append(item)
            else:
                item["reason"] = "same declared kind; representation differs"
                adapters.append(item)

    return exact, adapters


def _match_interfaces(
    source: dict[str, Any],
    destination: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    exact: list[dict[str, Any]] = []
    adapters: list[dict[str, Any]] = []

    emitted = [x for x in source.get("interfaces", []) if x.get("direction") == "emit"]
    accepted = [x for x in destination.get("interfaces", []) if x.get("direction") == "accept"]

    for output in emitted:
        for input_ in accepted:
            if output.get("kind") != input_.get("kind"):
                continue
            item = {
                "from_world": source["owner"]["world"],
                "to_world": destination["owner"]["world"],
                "kind": output["kind"],
                "emitted": _repr_key(output),
                "accepted": _repr_key(input_),
            }
            if _decl_key(output) == _decl_key(input_):
                item["protocol"] = output["protocol"]
                item["version"] = output["version"]
                item.pop("emitted")
                item.pop("accepted")
                exact.append(item)
            else:
                item["reason"] = "same declared kind; representation differs"
                adapters.append(item)

    return exact, adapters


def _sorted_unique(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[bytes] = set()
    result: list[dict[str, Any]] = []
    for record in sorted(records, key=_canonical_bytes):
        key = _canonical_bytes(record)
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def compare_charts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    for label, chart in (("left", left), ("right", right)):
        errors = validate_chart(chart)
        if errors:
            raise BodyOverlapError(label + " chart invalid:\n" + "\n".join("- " + e for e in errors))

    need_offer: list[dict[str, Any]] = []
    exact_interfaces: list[dict[str, Any]] = []
    adapters: list[dict[str, Any]] = []

    for source, destination in ((left, right), (right, left)):
        matches, declaration_adapters = _match_declarations(source, destination)
        need_offer.extend(matches)
        adapters.extend(declaration_adapters)

        interface_matches, interface_adapters = _match_interfaces(source, destination)
        exact_interfaces.extend(interface_matches)
        adapters.extend(interface_adapters)

    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "left_chart": {
            "chart_id": chart_id(left),
            "world": left["owner"]["world"],
            "occurrence": left["owner"]["occurrence"],
        },
        "right_chart": {
            "chart_id": chart_id(right),
            "world": right["owner"]["world"],
            "occurrence": right["owner"]["occurrence"],
        },
        "exact_interfaces": _sorted_unique(exact_interfaces),
        "need_offer_matches": _sorted_unique(need_offer),
        "adapter_candidates": _sorted_unique(adapters),
        "conflicts": [],
        "unresolved": [],
        "authority": "none",
        "non_promotions": [
            "overlap != identity",
            "compatibility != authority",
            "need != command",
            "offer != obligation",
            "receipt != constitutes",
        ],
    }
    receipt["receipt_id"] = receipt_id(receipt)
    return receipt


def _dump(value: Any, path: str | None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("left")
    root.add_argument("right")
    root.add_argument("--output")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        receipt = compare_charts(load_chart(args.left), load_chart(args.right))
    except BodyOverlapError as exc:
        sys.stderr.write(f"error:\n{exc}\n")
        return 1
    _dump(receipt, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
