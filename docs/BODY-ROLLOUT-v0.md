# BODY rollout register v0

This register tracks adoption of the Static Collective Body Surface Standard v0.

It is a rollout witness, not global project authority.

```text
listed != canonical
pending PR != adopted on main
unresolved != exempt
exempt != low value
```

## Default

Active Static Collective projects participate by default through:

```text
.body/surface-v0.json
```

A project that is specifically better without body participation publishes:

```text
.body/exemption-v0.json
```

Absence of both remains `UNRESOLVED`.

## Wave 0 — standard and executable substrate

| Project | State | PR |
| --- | --- | --- |
| Free Graph | pending adoption; standard + BODY-OVERLAP-001 + BODY-PULSE-001 + owner surface | #15 |

## Wave 1 — core organs

| Project | State | PR |
| --- | --- | --- |
| ALEX.2 | pending owner-surface adoption | #129 |
| 3rdi | pending owner-surface adoption | #32 |
| Dogram | pending owner-surface adoption | #141 |
| LOADOUT | pending owner-surface adoption | #20 |

## Wave 2 — active neighboring organs

| Project | State | PR |
| --- | --- | --- |
| Project0 | pending owner-surface adoption | #67 |
| TranchNode | pending owner-surface adoption | #77 |
| Corpus OS | pending owner-surface adoption; interface list intentionally empty | #34 |
| Band Runtime | pending owner-surface adoption; interface list intentionally empty | #20 |
| Haunted Phonograph | pending owner-surface adoption; ResolvedPerformance version left unresolved | #25 |
| Static Live | pending owner-surface adoption; Performance Packet v0.1 declared | #10 |
| Haunted Toaster | pending owner-surface adoption; BETA cross-project protocol nomination left unresolved | #292 |
| The Daily Slice | pending owner-surface adoption; witness layer declares no machine handoff yet | #71 |

## Audited but not yet classified

### Autodiscography Vault

Despite the word `vault`, this is an active executable preservation instrument, not a static archive. Its current README describes a browser/local acquisition membrane, exact-byte admission, append-only receipts, and a Corpus OS handoff.

Therefore:

```text
repo name suggests archive
!=
evidence for body exemption
```

Status remains `UNRESOLVED` until its trust boundary is specifically translated into a body surface.

### Empty repositories

An empty or placeholder repository is not automatically exempt. It may later become active. Until purpose is attributable, status remains `UNRESOLVED`.

### Private repositories

Private visibility is not itself an exemption. A private project may publish a local-only body surface if doing so does not widen disclosure. Privacy-sensitive projects can instead use `body.exemption/v0`.

## Next-wave selection rule

Prefer inspection in this order:

1. projects with existing cross-repo handoffs;
2. projects with executable machine-readable contracts;
3. active products and research organs;
4. creative/output projects with meaningful machine surfaces;
5. private projects after disclosure review;
6. legacy variants, mirrors, and historical experiments only when they are still operationally relevant.

Do not roll out by filename pattern or repository age alone.

## Current exemption count

No project has yet been shown, from inspected owner evidence, to require exemption.

The exemption path remains available and machine-readable; it should be used when evidence supports it rather than to reduce rollout work.
