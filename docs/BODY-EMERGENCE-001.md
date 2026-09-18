# BODY-EMERGENCE-001 — Two-Layer Development Method

## Purpose

BODY-EMERGENCE-001 is a cross-repository development method for helping independently owned organs discover useful joins without inventing a central authority, global truth store, or master planner.

The method has two layers:

```text
LAYER 1 — LOCAL CHARTS
what this organ can lawfully witness, provide, need, and do at this occurrence

LAYER 2 — BODY PROJECTION
a no-promotion projection of overlaps, missing joins, and candidate bridges among charts
```

The body is not declared into existence. It is approached through repeated local operation, witnessed overlap, bounded joining, and retained receipts.

Core law:

> **Global coherence may emerge from local operation. No global projection silently becomes local authority.**

This is a development method, not a metaphysical claim.

---

## Why this belongs beside Free Graph

Free Graph already preserves relations without centralizing truth or authority:

> Provenance may travel. Authority stays local.

BODY-EMERGENCE-001 does not add a sixth portable relation verb. Body-specific semantics remain in packet extensions and local qualifiers until executable pressure justifies any future grammar change.

Free Graph owns the portable traversal projection only.

Neighboring organs retain their existing ownership:

- **ALEX.2** — provenance, derivation, source witnesses, research formation.
- **3rdi** — observer-local cuts and attributed projections.
- **Dogram** — deterministic calculation, deltas, ablations, reachability, comparison.
- **LOADOUT** — bounded world compilation, capability binding, effect fences, authorization.
- **Free Graph** — no-promotion relation topology and historical traversal.
- **Owning repositories / humans** — adoption, merge, publication, mutation, consequence.

```text
body projection != body authority
candidate join != admitted join
compatibility != permission
need != command
measure != rank
recurrence != canon
```

---

# Layer 1 — Local Chart

A Local Chart is an occurrence-bound description of one organ from its own lawful evidence.

A chart answers:

1. What is this organ, at this exact occurrence?
2. What can it provide?
3. What does it currently need?
4. What interfaces or protocols can it lawfully touch?
5. What is its bounded operational measure?
6. What receipts support those statements?
7. What authority remains explicitly absent?

A Local Chart SHOULD be derivable from owner-current evidence and SHOULD carry an exact source identity where available.

Conceptual shape:

```json
{
  "schema": "body.chart/v0",
  "owner": {
    "world": "repo-or-organ",
    "occurrence": "exact-sha-or-other-immutable-cut"
  },
  "provides": [],
  "needs": [],
  "interfaces": [],
  "measure": {
    "declared": [],
    "observed": []
  },
  "receipts": [],
  "residual_fog": [],
  "non_authorities": []
}
```

This shape is illustrative. v0 does not yet publish a canonical schema.

## Measure

**Measure is not a scalar quality score.**

A measure is a set of attributable, typed bounds describing how a local part may operate.

Examples:

- accepted input kinds;
- emitted output kinds;
- reachable effect classes;
- declared read/write surface;
- supported protocol versions;
- bounded context or work budget;
- observed test surface;
- freshness / occurrence bounds;
- explicit exclusions.

Every quantitative measure MUST retain:

```text
dimension + value + unit + provenance
```

when a numeric value is used.

A chart MUST NOT collapse heterogeneous dimensions into a single "importance", "fitness", "trust", or "body value" score.

```text
measure != worth
measure != authority
measure != global priority
```

---

# Layer 2 — Body Projection

A Body Projection is derived from two or more Local Charts.

It asks:

- Where do declared outputs and inputs overlap?
- Where does one chart declare a need another can satisfy?
- Which protocols already match?
- Which joins require an adapter?
- Which candidate bridges would create undeclared effects?
- Which needs currently have no neighboring offer?
- Which existing joins are single points of failure?
- Which apparent overlaps disappear when provenance or occurrence is held fixed?

A Body Projection is always provisional and no-promotion.

Conceptual shape:

```json
{
  "schema": "body.projection/v0",
  "charts": [],
  "candidate_overlaps": [],
  "unmet_needs": [],
  "bridge_candidates": [],
  "conflicts": [],
  "ablations": [],
  "residual_fog": [],
  "non_promotions": []
}
```

The projection may say:

> A and B expose compatible declared surfaces.

It may not say:

> A must integrate with B.

The projection may say:

> Removing bridge X disconnects these currently declared paths.

It may not say:

> X is indispensable in reality.

---

# Overlap

An overlap is a witnessed or computed compatibility relation between Local Charts.

Minimum useful overlap classes for v0:

```text
EXACT_INTERFACE
    an emitted type/protocol exactly matches an accepted type/protocol

NEED_OFFER
    one chart declares a need that another explicitly offers

SHARED_WITNESS
    charts lawfully refer to the same attributable source / artifact / receipt

ADAPTER_REQUIRED
    the semantic seam appears compatible but representation differs

CONFLICT
    the proposed join would violate a declared fence, version, effect, or authority boundary

UNRESOLVED
    insufficient current evidence to classify the relation
```

These are BODY-EMERGENCE-local qualifiers, not new Free Graph global verbs.

---

# The development loop

The method for ecosystem work is:

```text
1. CHART
   obtain owner-current local charts

2. PROJECT
   create a no-promotion body projection

3. FIND
   identify one strong overlap, unmet need, or structural bottleneck

4. MEASURE
   state the local operational bounds relevant to that seam

5. PRESSURE
   use Dogram / tests / hostile specimens to test the proposed relation

6. LOAD
   ask LOADOUT for the smallest bounded world capable of testing the join

7. JOIN
   implement one owner-approved, bounded bridge

8. RECEIPT
   retain exact change, checks, effects, refusals, and remaining fog

9. RECHART
   emit new local charts from the changed owner states

10. REPROJECT
    observe how the body topology changed
```

This produces a development cadence:

```text
LOCAL -> GLOBAL PROJECTION -> LOCAL ACTION -> GLOBAL DELTA
```

rather than:

```text
GLOBAL PLAN -> FORCE LOCAL CONFORMANCE
```

---

# What "accelerating body emergence" means operationally

The method does not attempt to maximize repository count, dependency count, integration count, or activity.

It tries to reduce four frictions:

## 1. Discovery friction

Useful neighboring organs should be discoverable from declared needs and offers without requiring a human to remember the entire ecosystem.

## 2. Translation friction

Representation mismatches should become explicit adapter candidates instead of vague "these repos should connect someday" notes.

## 3. Verification friction

Every proposed bridge should arrive with the smallest relevant pressure test and the receipts needed to check it.

## 4. Re-entry friction

After a change, the ecosystem should be able to recompute the local charts and body projection without reconstructing the project history from conversation memory.

Acceleration therefore means:

```text
less manual carrying between organs
+ faster discovery of lawful seams
+ smaller executable joins
+ better retained receipts
```

not automatic central coordination.

---

# Tool surface — target shape

A future executable surface could expose:

```text
body chart
    derive / validate one occurrence-bound Local Chart

body project
    compose charts into a no-promotion Body Projection

body overlaps
    list candidate overlaps with exact reasons

body gaps
    list declared needs with no current witnessed offer

body bridge
    emit an inert bridge proposal:
      source chart
      destination chart
      interface delta
      required adapter
      required tests
      effect boundary
      unresolved questions

body ablate
    remove one chart or overlap from the projection
    and calculate the resulting topology delta

body pulse
    recompute a fresh projection from current attributable charts
```

No v0 command may mutate an owning repository merely because it found an overlap.

```text
discover != bind
project != execute
bridge proposal != bridge
body pulse != watcher authority
```

---

# First executable slice

The smallest useful proof is **BODY-OVERLAP-001**.

Input:

- two hand-authored Local Charts;
- each with exact owner occurrence;
- declared `provides`, `needs`, and `interfaces`.

Operation:

1. validate required chart fields;
2. compare provides -> needs;
3. compare emitted -> accepted interfaces;
4. classify exact matches, adapter-required seams, conflicts, and unresolved relations;
5. emit a deterministic projection receipt.

Output:

```json
{
  "schema": "body.overlap-receipt/v0",
  "left_chart": "...",
  "right_chart": "...",
  "exact_interfaces": [],
  "need_offer_matches": [],
  "adapter_candidates": [],
  "conflicts": [],
  "unresolved": []
}
```

Hostile controls MUST prove:

- same label with incompatible protocol version is not an exact match;
- shared filename is not shared semantic interface;
- a declared need does not authorize the offering organ;
- an overlap does not create a `constitutes` relation;
- missing occurrence identity cannot be silently treated as current;
- repeated overlap does not manufacture canon.

---

# Mapping onto existing Static Collective organs

## 3rdi -> Local Chart aperture

3rdi already asks what is lawfully visible to an observer at a cut. A BODY chart can consume a 3rdi projection or use the same occurrence discipline without making 3rdi own ecosystem semantics.

```text
3rdi projection -> chart evidence
chart != 3rdi authority
```

## ALEX.2 -> provenance spine

ALEX can support the claims inside a chart:

```text
"provides protocol X"
"needs adapter Y"
"tested at commit Z"
```

without allowing interpretation to overwrite source evidence.

## Free Graph -> body topology

Free Graph can carry charts and candidate overlaps using existing `connects`, `tests`, `bears-on`, and owner-local `constitutes` only when an owner actually gates an adoption.

No global "body edge" is required.

## Dogram -> measure and pressure

Dogram is well suited to:

- compare chart deltas;
- ablate one organ / edge;
- calculate reachability changes;
- distinguish same-surface / different-history cases;
- pressure candidate overlap classifications.

Dogram reports the delta and keeps the receipt. It does not decide whether a bridge should be built.

## LOADOUT -> lawful join

When a candidate seam is selected for implementation, LOADOUT compiles the smallest world capable of testing or building it.

```text
body discovers candidate
    ->
LOADOUT determines lawful executable world
    ->
owner gate admits/refuses
    ->
implementation
    ->
new receipts
    ->
rechart
```

---

# Emergence invariants

BODY-EMERGENCE-001 adopts these invariants:

```text
LOCAL CHART != GLOBAL BODY
GLOBAL BODY PROJECTION != REALITY
OVERLAP != IDENTITY
COMPATIBILITY != AUTHORITY
MEASURE != WORTH
NEED != COMMAND
OFFER != OBLIGATION
JOIN != MERGE OF OWNERSHIP
FREQUENCY != IMPORTANCE
CENTRALITY != CANON
ABSENCE FROM PROJECTION != NONEXISTENCE
PROJECTION DELTA != CAUSAL EXPLANATION
```

The target is a body whose parts remain attributable parts.

---

# Design test

The method succeeds when the ecosystem can answer this question mechanically:

> **Given the current attributable states of several organs, what is the smallest useful join we can test next, why does it appear compatible, what measure bounds each side, what authority is still required, and what changes in the projected body if the join succeeds?**

The machine may assemble the evidence and calculate the topology.

The owning worlds still decide what becomes real.
