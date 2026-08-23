# Relational Coordinate / Projection Key v0

## Status

Proposed cross-project primitive. This note does **not** add a Free Graph relation verb, execution capability, authority class, or sigil runtime.

## Compression

> A stable coordinate may participate in several typed relational spaces without collapsing those projections into one meaning or allowing any projection to manufacture warrant.

The working object is:

```text
Σ = stable coordinate / sigil
O = Resolve(Σ, world_head)
L = {domain, relation, resolution, decoder_version}
P_L(O) -> typed projection
```

The key boundary is:

```text
projection != evidence != authority != consequence
```

A sigil is therefore not a bag of unrelated meanings. It is a compact stable junction through which an attributable object can be queried by typed, versioned decoders.

## Candidate projection spaces

The same stable coordinate may expose different lawful views under different lenses:

```text
mathematical  -> operator / magnitude / transform
 topological  -> boundary / nesting / adjacency
     lineage  -> ancestry / descent coordinate
   narrative  -> recurrence / transition / role
cryptographic -> digest / commitment / verification coordinate
 world-state  -> discoverability / reachability / local posture
```

No projection silently inherits the claims of another.

## Relational-key metaphor

A physical key does not contain the room. It establishes a relation with a particular lock.

Likewise:

```text
sigil + typed lens -> intelligible projection
```

The formal term should remain **relational coordinate** or **projection key** rather than cryptographic key. Cryptographic key would imply secrecy or capability that this primitive does not inherently possess.

## Observer is not semantic authority

An observer may select a lens, but the observer does not define that lens ad hoc.

A lawful projection should be attributable to explicit selector state:

- domain;
- relation or query class;
- resolution;
- decoder version;
- world/head used to resolve the coordinate.

This keeps contextual meaning falsifiable instead of reducing it to arbitrary interpretation.

## Lens change is not object change

Two operations must remain mechanically distinct:

```text
ViewRotate(L, Σ) -> another projection of the same O
```

versus:

```text
ObjectRotate(O) -> O'
```

Changing the lens does not create ancestry, mutate the object, or spend authority.

If `ROTATE`, `NEST`, `CUT`, `MERGE`, or another operator is constituted as a real object transformation inside a domain grammar, that transformation must leave its own attributable result/receipt.

## Free Graph fit

Free Graph already separates source digest, access/export posture, node/link status, and authority. It also keeps the five portable verbs small.

Relational-coordinate semantics should inherit that discipline:

- no sixth verb is introduced;
- domain-specific lens semantics remain in `qualifier` or `extensions` until executable pressure justifies promotion;
- selecting a projection cannot change a source's `access` or `export` posture;
- selecting a projection cannot promote `authority`;
- selecting a projection cannot convert a proposed claim into an observed/tested/supported/adopted one;
- a projection is historical testimony about what became legible under a declared lens, not proof that the projected claim is true.

## Sealed Witness fit

The sealed-witness pressure case is a particularly useful projection boundary.

A cryptographic/provenance lens may lawfully expose:

```text
stable source coordinate
commitment or digest
existence/timestamp witness
claimed relation
```

while the content projection remains closed.

That preserves the stronger rule:

> A source does not have to travel for its road to remain accountable.

It also preserves the correction:

```text
digest != hiding commitment
commitment != truth
existence witness != authority
```

## Five negative controls

Before this primitive deserves executable semantics, a specimen should pressure at least these cases.

### 1. Lens test

Hold `Σ` and `world_head` fixed. Change only `L`.

Expected: projections differ where the lens contract differs, while declared object identity and ancestry remain stable.

### 2. Object test

Hold `L` fixed. Change `Σ`.

Expected: the projection materially changes. The lens cannot carry the whole answer by itself.

### 3. Decoder-version test

Hold `Σ` and the nominal lens class fixed. Change `decoder_version`.

Expected: any changed projection is attributable to the new decoder version. Historical projections are not rewritten.

### 4. Authority test

Select every available lens against one object.

Expected: no lens selection increases authority, constitutes a relation, or creates execution capability without a separate owning-world gate.

### 5. Disclosure test

Resolve a sealed/private source through public-safe lenses.

Expected: a provenance/commitment projection may remain available while content remains redacted. Lens selection cannot widen `access` or `export`.

## Promotion rule

Do not promote this into schema/runtime merely because the model is elegant.

A candidate promotion should require:

1. at least one deterministic specimen implementing the five negative controls;
2. a second materially different consumer reproducing the same separation law;
3. no widening of the five Free Graph verbs merely to accommodate domain semantics;
4. explicit evidence that a projection primitive reduces ambiguity or duplication compared with ordinary typed fields.

Until then this remains a bounded design law:

> **One stable coordinate. Many lawful projections. No silent promotion between them.**
