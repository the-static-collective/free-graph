# Free Graph contract v0

## Purpose

Free Graph is a provenance-first **traversal graph**. Its strongest default claim is:

> This encounter, path, relation, question, test, result, or decision was witnessed here.

It does not own current project state. Owning worlds retain their own authority and gates.

## Five portable verbs

| Verb | Meaning |
| --- | --- |
| `connects` | A witnessed, proposed, inferred, or observed traversal relation. |
| `descends-from` | Attributable lineage, derivation, production, supersession, or transformation. |
| `tests` | A specimen applies declared pressure to a claim. |
| `bears-on` | A specimen result supports, refuses, or leaves a tested claim unresolved. |
| `constitutes` | An owning world's named gate adopts, refuses, or defers a local consequence. |

`connects`, `descends-from`, `tests`, and `bears-on` never carry `owner-local` authority.
Only `constitutes` may do so.

## Packet

`free-graph.packet/v0` contains content-addressed:

- `sources`
- `nodes`
- `links`

and task-scoped:

- `purpose`
- `modes`
- `scope`
- `task_world_cut`
- `residual_fog`
- `non_imports`

IDs are SHA-256 digests of canonical JSON with the record `id` omitted.

## Authority

- Provenance may travel; authority stays local.
- Reachable does not mean true, permitted, adopted, or current.
- Repetition does not manufacture canon.
- Resemblance does not prove ancestry.
- Research can bear on a claim without constituting project truth.
- A local adoption requires an owning world, named gate, owner-current head, and gate receipt.

## Task World Cut

Before `metabolize` or `prove`, the run selects the exact evidence neighborhood needed for the task and records omitted doors.

A cut may be:

- `sufficient`
- `unresolved`
- `not-required`

An `unresolved` cut is terminal for that run. It may not test, bear on, or constitute in the same run.

## Source export boundary

Public/exportable testimony may carry an excerpt or resolvable pointer.

Private or restricted testimony with `export: pointer-only` or `prohibited` may instead survive as:

- digest;
- lawful source coordinate;
- explicit `redaction`.

The public packet must not force disclosure of a private excerpt merely to preserve provenance.

## Local vocabulary

The global grammar stays small. Domain-specific predicates and evidence roles belong in `qualifier` or `extensions` until repeated executable pressure justifies a future version.

## Projection rules

`neighbors` creates a bounded traversal projection.
`merge` creates a set-union projection.

Neither operation promotes truth, currentness, or authority.

## History

Records are immutable by content address. Later support, refusal, supersession, or adoption is added as new records and relations; old testimony is not rewritten to make the present look ancestral.
