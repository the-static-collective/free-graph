# Free Graph

A provenance-first traversal substrate for remembering where thought traveled without centralizing truth or authority.

## Boundary

Free Graph records **historical testimony, relations, questions, tests, results, and local gate receipts**. It does not own current project state and it does not become a master graph for the Static Collective.

The portable law is:

> Provenance may travel. Authority stays local.

## v0 grammar

Five link verbs are portable:

- `connects`
- `descends-from`
- `tests`
- `bears-on`
- `constitutes`

See [`grammar/relation-v0.md`](grammar/relation-v0.md) and [`docs/contract-v0.md`](docs/contract-v0.md).

## Repository shape

```text
grammar/      portable relation vocabulary
laws/         substrate invariants
schema/       machine-readable packet contract
scripts/      validation, hashing, bounded traversal, projection merge
specimens/    public-safe pressure tests
tests/        executable contract checks
docs/         contract, public specimen boundary, implementation record
```

## Quick start

Validate a packet:

```bash
python3 scripts/fg.py validate specimens/wav-space-v0.public.json
```

Inspect a bounded neighborhood:

```bash
python3 scripts/fg.py neighbors PACKET.json NODE_ID --depth 1
```

Merge packets into a **no-promotion union projection**:

```bash
python3 scripts/fg.py merge A.json B.json --output union.json
```

Run the contract tests:

```bash
python3 -m unittest discover -s tests -v
```

Run the Promotion/Invariance Crucible:

```bash
python3 scripts/promotion_crucible.py \
  specimens/promotion-crucible-v0/case.json
```

The founding two-repository result is intentionally `split-required`; see [`docs/promotion-crucible-v0.md`](docs/promotion-crucible-v0.md).

## Public/private source boundary

A packet may preserve a private or restricted source as a digest-only redacted record when the source is non-portable (`pointer-only` or `prohibited`). This repo never requires publishing private excerpts merely to preserve provenance.

The included specimens are public-safe projections of private-source runs. Their original private excerpts were **not imported** into this public repository.

## Non-goals

Free Graph is not:

- a global authority registry;
- an always-current truth store;
- an ontology for every domain;
- a reasoner that silently promotes repeated claims;
- a substitute for project-owned gates, tests, receipts, or human witness.

Project-owned evidence remains authoritative about project-local current state.
