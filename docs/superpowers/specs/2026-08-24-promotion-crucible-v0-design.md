# Promotion/Invariance Crucible v0 Design

## Status

Accepted on 2026-08-24 for [Free Graph issue #5](https://github.com/the-static-collective/free-graph/issues/5).

The first expected result is deliberately not a certification. The attractive combined slogan fractures under translation: National Treasure can independently test its epistemic part, while Free Graph presently carries the stronger local constitutional claims. A `split-required` whole verdict is a successful discovery.

## Purpose

Build a reusable adversarial harness that asks whether a candidate cross-project invariant survives translation or merely leaks shared vocabulary.

The crucible must:

- compare materially different implementations, not renamed wrappers;
- evaluate operational behavior instead of trusting self-description;
- test clauses independently;
- preserve local semantics and receipt shapes;
- refuse a copied-vocabulary poison specimen;
- return a productive missing discriminator for every unsupported clause;
- never average clause results into an aggregate score or green badge.

The promotion threshold is:

> Frequency is not the threshold. Survival under translation is.

## Candidate law and clause decomposition

The candidate law is a conjunction of five independently tested clauses.

### Epistemic clause

Projection alone does not increase what the underlying evidence identifies.

Operationally: when the underlying source set is unchanged, deterministic re-expression cannot shrink the compatible-world set. A smaller set is lawful only when a separately attributable new source or discriminator is present.

### Authority clause

Projection alone does not increase warrant, permission, or local authority.

Operationally: if effective warrant rises, the receipt must name a separate local gate. A declaration such as `projectionAuthority: "none"` does not excuse behavior that unlocks an action.

### Consequence clause

Projection alone does not constitute a consequential state change. Any consequence requires an independently named local gate.

A projection may participate in a lawful causal chain:

```text
projection -> human/system observes -> named local gate -> action -> consequence
```

The forbidden shortcut is:

```text
projection -> therefore consequence
```

The crucible must therefore accept a state change with a separately attributable gate receipt and refuse the same state change without one. It must not require projections to be causally inert.

### Historical clause

Decoder or lens changes append attributable projections rather than rewriting prior projections as though they had always existed.

Operationally: prior projection identifiers remain present and byte-stable; changed output receives a new projection identifier with decoder version and derivation attribution.

### Identity clause

Representation or lens change does not silently become object or worldline change.

Operationally: a view operation preserves object and worldline identifiers. A changed identity requires a separately attributable object-transform receipt.

## Harness boundary

The harness uses a local `promotion-crucible.case/v0` format and emits `promotion-crucible.receipt/v0`.

This does not modify `free-graph.packet/v0`, add a sixth Free Graph verb, add an authority class, or introduce a service/database/runtime. Promotion results remain testimony, not adoption.

## Consumers

### Free Graph relational-coordinate consumer

An executable fixture in this repository implements all five clauses in Free Graph's own projection vocabulary. It supplies both lawful and negative controls, including:

- unchanged compatible worlds under re-expression;
- no warrant rise from lens selection;
- a lawful gate-mediated consequence;
- an unlawful ungated consequence;
- append-only decoder history;
- stable object/worldline identity under a lens change.

This is one embodiment, not enough for portability by itself.

### National Treasure SSW-MATH-001 consumer

The second repository remains implementation-independent and vocabulary-independent. The crucible pins National Treasure commit:

```text
65e67062a3be933332db36af8bc095fc9b2660b4
```

and adapts the native `ssw-math.receipt/v0` testimony from:

```text
cases/same-state-different-world/specimens/ssw-math-001/receipt.json
```

The adapter tests only what that domain actually earns:

- the supplied observation leaves two distinct compatible worlds;
- deterministic re-expressions preserve the collision;
- graph identities remain distinct even when observations coincide.

It does not translate National Treasure's mathematical testimony into Free Graph authority, consequence, or history claims.

### Mandatory poison consumer

The poison imports none of Free Graph's code but deliberately copies its nouns and receipt silhouette. It declares:

```json
{"projectionAuthority": "none"}
```

while its operational trace raises effective warrant, unlocks an action, and changes state without a separately attributable local gate.

The poison is an attack, not portability evidence. The crucible must refuse the authority and consequence behaviors even though the artifacts look homologous. If it accepts the poison because of the copied names or declaration, crucible integrity fails.

## Material-difference rule

Two supports count as independent translation evidence only when all of these differ:

- repository/source revision;
- implementation family;
- native vocabulary family;
- native receipt shape.

A second wrapper over the same implementation does not count. Neither a poison nor an adapter-authored relabeling counts as an embodiment.

Different words with the same observable constraint are positive evidence. Same words with reversed behavior are negative evidence.

## Normalized operational witness

Adapters expose a small behavior trace to the evaluator. The trace is not a portable domain schema; it is harness-local test input.

| Clause | Behavior inspected | Required separately attributable receipt |
| --- | --- | --- |
| epistemic | compatible worlds before/after; underlying source IDs before/after | new source/discriminator when compatible worlds shrink |
| authority | effective warrant before/after | local gate when warrant rises |
| consequence | consequential state before/after | local gate when state changes |
| historical | prior projection IDs/content before/after; decoder version | new projection attribution for changed decoder output |
| identity | operation kind; object/worldline IDs before/after | object-transform receipt when identity changes |

Self-described policy fields are retained for the attack receipt but never used to decide compliance.

## Clause verdicts

Each clause receives exactly one of:

- `supports`: at least two materially different positive embodiments satisfy the clause and no positive embodiment refuses it;
- `only-one-domain`: exactly one independent positive embodiment satisfies it;
- `unresolved`: no sufficient positive embodiment exists;
- `refuses`: at least one positive embodiment contradicts the clause.

Poison results are reported separately as attack outcomes. A poison correctly refused does not count toward the two-embodiment threshold.

The whole candidate has no score and no aggregate green. The v0 whole verdict is:

- `crucible-refused` if a mandatory vocabulary-leak poison is not refused on every required operational behavior;
- `portable-candidate` only if every clause independently returns `supports` and all mandatory attacks are caught;
- otherwise `split-required`.

This is conjunction, not averaging. Four portable clauses plus one local clause are two laws hiding inside one sentence, not an 80% portable law.

## Expected v0 result

| Clause | Expected verdict | Reason |
| --- | --- | --- |
| epistemic | `supports` | Free Graph and native SSW independently preserve the compatible-world set under re-expression |
| identity | `supports` | Free Graph preserves object/worldline identity; SSW preserves two graph identities despite equal observations |
| authority | `only-one-domain` | only Free Graph presently supplies a constitutional warrant control |
| consequence | `only-one-domain` | only Free Graph presently supplies the separately attributable gate control |
| historical | `only-one-domain` | only Free Graph presently supplies append-only decoder history |
| whole | `split-required` | the conjunction does not yet survive translation |

## Productive refusal

Every non-`supports` clause must name:

- the semantic fracture;
- the evidence currently present;
- the missing discriminator;
- one materially different specimen that could decide it.

For example, the missing consequence discriminator is a non-Free-Graph consumer whose native system both (a) permits representation output to participate in a causal path and (b) proves consequential state change requires a separately attributable local decision gate.

## Determinism and provenance

The receipt must include:

- a digest of the complete case;
- pinned source revisions and native receipt digests;
- per-consumer operational checks;
- per-clause verdicts and evidence IDs;
- mandatory attack outcomes;
- missing discriminators;
- an explicit `aggregate_score: null` refusal marker;
- a deterministic whole verdict.

Repeated runs over the same case must be byte-identical.

## Non-claims

- This v0 result does not promote the five-clause conjunction.
- It does not adopt a law into any owner project.
- It does not prove that two domains are universally sufficient for future promotion decisions.
- It does not make projections causally inert.
- It does not infer behavior from words, declared policy, or receipt shape.
- It does not close Free Graph issue #2; it consumes that issue's pressure as one local embodiment.
