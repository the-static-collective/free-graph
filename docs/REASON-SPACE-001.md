# REASON-SPACE-001 — The logic of a journey, not the logic of a pipeline

**Research proposal with executable Free Graph v0 projection**, anchored to the actual source-owned [MOTIF MAP-002 investigation](https://github.com/the-static-collective/MOTIF/pull/74).

## Why this is more abstract than wiring four named tools

MOTIF should not need to hardcode `ALEX -> planZ -> Dogram -> GRAFT` as a permanent route. Different questions may require different methods, parallel or non-sequential investigation, or **no** additional investigation.

Instead, each *bounded reason trail* preserves typed events and accountable relations:

```
Question --connects--> Hypothesis
                             ^
Probe --tests----------------|
                             
Finding --bears-on(refuses/unresolved/supports)--> Hypothesis
Next question --connects--> Original question
```

A traversal edge is **not** an executable adapter, causal proof, epistemic warrant, machine permission, or current owner-selected version. An unresolved hypothesis retains its fog even if a graph model becomes reachable.

This implementation deliberately uses the **existing Free Graph v0 packet schema**, its original content-addressed records and its original five verbs. It does **not** invent a sixth verb. `constitutes` is explicitly unavailable to this generic bridge: an owner-local decision needs its real world head and gate receipt, not an AI inference.

### Generic protocol

`scripts/reason_space.py` accepts `free-graph.reason-trail/v0` with:
- one bounded question;
- public source coordinates (SHA-256 and exact Git revision, **source-declared** until independently verified);
- named `question/hypothesis/probe/finding/next` events with statuses;
- `connects/descends-from/tests/bears-on` relations (bearing on a claim requires an attributable specimen-receipt source);
- explicit unresolved fog.

It produces a valid `free-graph.packet/v0` in **`re-enter` mode with an unresolved Task World Cut**. No private source, excerpts from personal material, owner-local gate, network request, external account access, execution or deployment is generated. Public source pointers do not prove the source contents are true. The caller is responsible for verifying source hashes and permissions; the converter marks source pointers **not independently verified by the generic converter**.

The independently selectable **`all`**, **`evidence`**, and **`next`** lenses rotate the *view*, not the original history. Original node IDs remain identical across projections. A lens never increases authority or concludes a new fact. The packet IDs correctly change because the views differ.

### Real, source-pinned MOTIF specimen

`scripts/motif_reason_bridge.py` is an independent materialization adapter for [MOTIF's actual native-court report](https://github.com/the-static-collective/MOTIF/blob/research/map-of-maps-002-native-inquiry-court/fieldwork/map-of-maps-002/evidence/first-actual-native-court-2026-11-05.json). It verifies the exact Git blob SHA-1 **before** translating that publicly archived JSON. It checks the original report's non-authority dispositions and reads the native findings from **ALEX, planZ, Dogram, GRAFT** plus the original planZ/PlayDeck contract inspection. It constructs question, claim, probes, findings, and a next proposed investigation, with original source-locus pointers.

The recorded case is deliberately **unresolved**:
- planZ calculated a seven-step *hypothetical* research plan, not an executed plan;
- ALEX's source-owned evaluator refused attention as proof of a claim;
- Dogram's hypothetical graph-edge addition changed reachability, **not interoperability**;
- GRAFT's native scout examined two public docs **offline** through a simulated GitHub API, not live browsing;
- PlayDeck receipt validation was inspected as source code, **not executed**;
- no genuine rendered full-performance receipt was established and no cross-owner adapter was implemented.

### Executable replay

The CI workflow checks out the exact original public MOTIF report at pinned commit `070aba60319cbab3d1c1838ec7481c350e7d86e5`, hashes the Git blob, and produces three complete Free Graph v0 JSON packets in an artifact:

```sh
python3 scripts/motif_reason_bridge.py native-motif/fieldwork/map-of-maps-002/evidence/first-actual-native-court-2026-11-05.json \
  --lens all --output /tmp/reason-all.json
python3 scripts/fg.py validate /tmp/reason-all.json
python3 scripts/motif_reason_bridge.py native-motif/fieldwork/map-of-maps-002/evidence/first-actual-native-court-2026-11-05.json \
  --lens evidence --output /tmp/reason-evidence.json
python3 scripts/motif_reason_bridge.py native-motif/fieldwork/map-of-maps-002/evidence/first-actual-native-court-2026-11-05.json \
  --lens next --output /tmp/reason-next.json
```

Local contract tests exercise data tampering, source/branch spoofing, unauthorized verbs, false owner-adoption, provenance gaps, changed claim identities, lineage cycles and lens invariance.

**What this does NOT prove:** generic autonomous tool selection, unrestricted repository discovery, genuine independent causal understanding or automatic adaptation. These require new experiments with separately authored unseen tasks. This project supplies a small, reusable, source-conscious *representation of reasoning journeys*, and the first working conversion of an actual MOTIF investigation.

**Principle:** The same source may be inspected through many lawful lenses; selecting a lens does not change its history, evidence quality, currentness, or authority.
