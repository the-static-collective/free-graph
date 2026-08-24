#!/usr/bin/env python3
"""Emit a deceptive projection receipt whose behavior contradicts its declaration."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def run_poison_consumer() -> dict[str, Any]:
    projection = {
        "id": "projection:poison-owner-view-v1",
        "kind": "owner-view",
        "decoderVersion": "poison-decoder/v1",
    }
    local_state = {
        "effectiveWarrant": "none",
        "locked": True,
        "actionUnlocked": False,
    }
    warrant_before = local_state["effectiveWarrant"]
    state_before = "locked" if local_state["locked"] else "unlocked"

    # Deliberate defect: observing the projection directly unlocks the action.
    if projection["kind"] == "owner-view":
        local_state["effectiveWarrant"] = "owner-local"
        local_state["locked"] = False
        local_state["actionUnlocked"] = True

    return {
        "receiptSchema": "free-graph.relational-coordinate.receipt/v0",
        "projectionAuthority": "none",
        "projectionConsequence": "requires-local-gate",
        "projection": projection,
        "operationalTrace": {
            "effectiveWarrantBefore": warrant_before,
            "effectiveWarrantAfter": local_state["effectiveWarrant"],
            "actionUnlocked": local_state["actionUnlocked"],
            "stateBefore": state_before,
            "stateAfter": "locked" if local_state["locked"] else "unlocked",
            "gateReceipts": [],
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    rendered = json.dumps(run_poison_consumer(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
