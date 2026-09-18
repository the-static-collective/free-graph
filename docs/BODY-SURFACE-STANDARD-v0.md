# Static Collective Body Surface Standard v0

## Status

**Default for active Static Collective projects.**

An active project SHOULD participate in BODY-EMERGENCE by publishing:

```text
.body/surface-v0.json
```

If participation would be misleading, unsafe, privacy-sensitive, or structurally wrong for the project, it SHOULD instead publish:

```text
.body/exemption-v0.json
```

Absence of both files means **UNRESOLVED**, never exempt.

## Purpose

The standard lets independently owned projects declare the smallest stable interface surface needed for body-level discovery.

A surface answers only:

- what this organ can provide;
- what it currently needs from neighboring organs;
- what interfaces it can emit or accept;
- what bounded operational measures describe those interfaces;
- what owner evidence supports the declaration;
- what the declaration explicitly does not authorize.

A surface does not grant execution, mutation, merge, publication, truth, evidence, or authority.

```text
surface != runtime
surface != capability grant
surface != authorization
surface != truth
surface != body authority
compatibility != obligation
need != command
```

## Two-layer rule

BODY-EMERGENCE keeps two layers distinct:

```text
OWNER LAYER
    .body/surface-v0.json
    stable owner-published interface declaration

OCCURRENCE LAYER
    exact SHA / immutable cut
    bound by BODY-PULSE when a chart is derived
```

The stable surface MUST NOT pretend to be current merely because it exists. A pulse binds the surface to an attributable occurrence and produces an occurrence-bound `body.chart/v0`.

## Required surface

A participating project publishes one `body.surface/v0` document conforming to:

```text
schema/body-surface-v0.schema.json
```

Required conceptual fields:

```text
schema
organ
owner
publication
provides
needs
interfaces
measure
receipts
residual_fog
non_authorities
evidence
authority = none
```

### Provides / needs

Declarations use the triple:

```text
kind + protocol + version
```

Matching labels or filenames are insufficient.

### Interfaces

Interfaces add direction:

```text
emit | accept
```

An exact body overlap requires compatible kind, protocol, and version.

### Measure

Measure describes bounded operational capacity. It is not a scalar quality or importance score.

```text
measure != worth
measure != authority
measure != project priority
centrality != canon
```

When numeric, a measure SHOULD preserve dimension, value, unit, and provenance.

## Exemption

A project that should not participate publishes `body.exemption/v0` conforming to:

```text
schema/body-exemption-v0.schema.json
```

The exemption MUST preserve:

- owner and organ;
- a reason code;
- a human-readable reason;
- a review trigger describing when the exemption should be reconsidered;
- `authority = none`.

Typical reasons include:

- static or historical archive;
- privacy-sensitive internal material where even interface publication leaks too much;
- intentionally standalone experiment;
- artifact repository that is not itself an operating project;
- authority boundary that should not be represented as interoperable.

Exemption is local and revisable. It is not a judgment of project value.

## Default-on rule for new projects

A newly created active Static Collective project SHOULD start with a body surface.

The initial surface may be minimal:

```json
{
  "schema": "body.surface/v0",
  "organ": "example",
  "owner": "the-static-collective/example",
  "publication": {
    "status": "owner-published",
    "standard": "static-collective/body-surface/v0",
    "scope": "interface-declaration"
  },
  "provides": [],
  "needs": [],
  "interfaces": [],
  "measure": {
    "declared": [],
    "observed": []
  },
  "receipts": [],
  "residual_fog": [
    "Initial surface has not yet discovered neighboring interfaces."
  ],
  "non_authorities": [
    "surface compatibility != authority"
  ],
  "evidence": [],
  "authority": "none"
}
```

Empty declarations are preferable to invented connectivity.

## Change discipline

A body surface is an owner interface declaration.

Changes SHOULD be reviewed when they:

- add or remove a provided protocol;
- add or remove a declared need;
- change protocol version;
- widen reachable effect expectations;
- remove a non-authority;
- materially change an operational measure.

Historical pulses retain the earlier surface through their occurrence-bound chart identity. Updating the current surface does not rewrite earlier body states.

## Discovery and execution

The standard preserves the existing organ boundaries:

```text
owner surface
    -> BODY-PULSE / Free Graph projection
    -> candidate overlap
    -> Dogram pressure where useful
    -> LOADOUT bounded executable world
    -> owner gate
    -> local implementation
    -> receipt
    -> new owner occurrence
    -> new pulse
```

No body projection may mutate an owner merely because it discovers compatibility.

## Rollout rule

For existing projects:

1. Active executable/research organs: participate by default.
2. Active creative/output projects: participate when they expose a meaningful machine or handoff surface.
3. Archives, vaults, historical mirrors, and intentionally inert collections: exemption is usually preferable.
4. Private projects: participation depends on whether a public or local-only surface can be published without leaking sensitive structure.
5. Unclear cases remain unresolved until inspected; they are not automatically classified.

The first adopted wave is Free Graph, ALEX.2, 3rdi, Dogram, and LOADOUT.

## Core invariants

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
