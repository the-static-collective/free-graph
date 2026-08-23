# Free Graph repository v0 design

**Date:** 2026-08-23

## Goal

Graduate Free Graph from a conversation/skill substrate into an independent, public repository that owns only the portable graph contract and executable validation mechanics.

## Constitutional boundary

The repository owns:

- the five-verb portable relation grammar;
- packet addressing and schema rules;
- provenance/authority invariants;
- deterministic validation and projection tools;
- public-safe specimens that pressure the contract.

The repository does not own:

- current truth in participating projects;
- cross-project authority;
- domain-specific ontologies;
- the ChatGPT skill's tool routing or invocation policy;
- private source excerpts whose export policy forbids publication.

## Architecture

`free-graph.packet/v0` is the machine contract. Records are content-addressed. `scripts/fg.py` validates packet structure and authority boundaries, rehashes temporary IDs, creates bounded neighborhood projections, and makes no-promotion packet unions.

Domain-specific semantics stay under `qualifier` and `extensions` unless repeated executable pressure justifies a future contract revision.

## First pressure result

The Bandcamp archaeology seed used richer local vocabulary than the core contract: domain source roles, interpretive claim labels, and colloquial `bears-on` relations. The repo does not widen the global grammar to absorb those local terms.

Instead, the public specimen maps:

- domain source roles -> `source_class: direct-observation` plus `extensions.source_role`;
- interpretive claims -> `claim_class: inferential` plus `extensions.claim_role`;
- non-test uses of `bears-on` -> `connects` plus a preserved qualifier/extension.

The pressure did reveal one core defect: private pointer-only sources could not be represented without embedding an excerpt or a resolvable pointer. v0 therefore explicitly permits digest-only redacted private/restricted records when export is `pointer-only` or `prohibited`.

## Verification

The initial gate requires:

1. unit tests for core authority/privacy invariants;
2. both public specimens validate;
3. the validator rejects public digest-only sources without an excerpt/pointer;
4. no private excerpt from the supplied source packets is present in the public specimen files.
