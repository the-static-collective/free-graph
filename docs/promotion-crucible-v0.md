# Promotion/Invariance Crucible v0

## Result

The founding candidate does not survive translation as one indivisible invariant.

```text
EPISTEMIC:  supports
HISTORY:    only-one-domain
AUTHORITY:  only-one-domain
CONSEQUENCE: only-one-domain
IDENTITY:   supports
WHOLE:      split-required
```

This is the intended successful result. There is no average, percentage, or aggregate green: the emitted `aggregate_score` is `null`, and the whole is derived by conjunction.

The executable receipt is [`specimens/promotion-crucible-v0/receipt.json`](../specimens/promotion-crucible-v0/receipt.json). Its case digest is:

```text
sha256:27cbabcb48da2891b593729abfe4ba434efe40299cabf3f0c07ed6dd91c9250d
```

## What survived translation

### Epistemic clause — `supports`

> Projection alone does not increase what the underlying evidence identifies.

Free Graph's local relational-coordinate fixture preserves the compatible-world set when it re-expresses an unchanged observation.

National Treasure independently reaches the same observable constraint in finite graph vocabulary. Its native `ssw-math.receipt/v0` shows that `C6` and two disjoint triangles have the same supplied vertex count, edge count, and degree sequence; deterministic re-expressions preserve that collision. Only the new connectedness discriminator separates them.

National Treasure imports none of Free Graph's code, schema, constitutional vocabulary, or receipt shape.

### Identity clause — `supports`

> Representation or lens change does not silently become object or worldline change.

Free Graph's view operation preserves object and worldline IDs; a changed object requires an explicit transform receipt.

National Treasure preserves two non-isomorphic graph identities even though their supplied observations coincide. Equality of representation does not merge the candidate worlds.

## What did not yet survive translation

### Authority clause — `only-one-domain`

Free Graph demonstrates that lens selection leaves effective warrant unchanged, while a warrant increase is lawful only through a separately attributable owner-local gate.

Semantic fracture: National Treasure's mathematical receipt contains no native warrant or permission transition.

Missing discriminator: a materially different consumer with a native authorization model must prove that representation output cannot unlock an action without its own attributable local gate.

### Consequence clause — `only-one-domain`

> Projection alone does not constitute a consequential state change; any consequence requires an independently named local gate.

The Free Graph fixture includes both sides:

- projection with no state change and no gate;
- projection observed in a lawful causal path whose state change is attributed to a separate local gate.

It also refuses an ungated state change. This does not make projections causally inert.

Semantic fracture: National Treasure's mathematical receipt is observational; it contains no native causal transition or decision gate.

Missing discriminator: a materially different consumer must let a representation participate in a causal path while proving the consequential transition belongs to a separate native gate.

### Historical clause — `only-one-domain`

Free Graph preserves the prior projection ID, content digest, and decoder version byte-for-byte while appending a newly identified, newly versioned projection. Reusing or rewriting the old ID is refused.

Semantic fracture: the National Treasure founding receipt has one evaluation history and no decoder-version succession.

Missing discriminator: a materially different append-only consumer must retain its old rendering while a changed decoder emits an attributable new rendering.

## Mandatory poison

`poison_consumer.py` is a standalone implementation that imports no Free Graph code. It deliberately emits the copied receipt silhouette and declarations:

```json
{
  "projectionAuthority": "none",
  "projectionConsequence": "requires-local-gate"
}
```

Its behavior does the reverse: observing its projection raises effective warrant to `owner-local`, unlocks the action, and changes `locked` to `unlocked` with an empty `gateReceipts` list.

The crucible ignores the declarations and evaluates the operational trace. It refuses both `authority` and `consequence`; the mandatory attack outcome is `caught`. The generated poison receipt is digest-pinned:

```text
sha256:3b054675a57ea2a4329d799d9e352e50cc61d112dc3383bd584106b3af5abaab
```

The poison is an integrity attack, never a positive portability embodiment.

## Source floor

| Source | Immutable pin | Role |
| --- | --- | --- |
| Free Graph relational-coordinate pressure | `50f8c5298150f04e7bf08dc29b70e500ccb36880` | local five-clause embodiment |
| National Treasure SSW-MATH-001 | `65e67062a3be933332db36af8bc095fc9b2660b4` | independent epistemic and identity embodiment |
| Native SSW receipt | `sha256:45ae6d1ff7fb29358320ff637d53a3594422d60d68ace7aa4546fc25ecbfb447` | unedited native testimony |
| Blackwell (1953) | [`10.1214/aoms/1177729032`](https://doi.org/10.1214/aoms/1177729032) | research lineage for experiment comparison and stochastic transformation |

Blackwell supplies conceptual ancestry, not the executable graph proof and not the repository-local constitutional clauses. The finite witness and its minimum discriminator are checked independently in National Treasure.

## Reproduce

```bash
python3 specimens/promotion-crucible-v0/poison_consumer.py \
  --output specimens/promotion-crucible-v0/poison-receipt.json

python3 scripts/promotion_crucible.py \
  specimens/promotion-crucible-v0/case.json \
  --output specimens/promotion-crucible-v0/receipt.json

python3 -m unittest tests.test_promotion_crucible -v
```

Repeated runs emit byte-identical receipts.

## Contract boundary

- The harness format is `promotion-crucible.case/v0`; it is not a Free Graph packet schema change.
- The five Free Graph verbs remain unchanged.
- The result is testimony about translation pressure, not adoption by an owner project.
- Free Graph issue #2 remains open; this harness consumes its pressure but does not pretend to complete its full specimen.
- The combined candidate remains split until each local clause gains an independently material second embodiment.
