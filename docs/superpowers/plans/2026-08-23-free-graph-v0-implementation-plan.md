# Free Graph v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a minimal, executable Free Graph v0 repository with a stable portable contract, privacy-safe provenance handling, and validating specimens.

**Architecture:** Keep the portable grammar deliberately small and put local semantics in `qualifier`/`extensions`. Use one standard-library Python CLI as the executable gate, backed by a JSON Schema and stdlib unit tests. Public specimens preserve private-source provenance by digest and redaction rather than publishing forbidden excerpts.

**Tech Stack:** Python 3 standard library, JSON Schema draft 2020-12, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-23-free-graph-repo-design.md`

## Global Constraints

- Provenance may travel; authority stays local.
- The global relation grammar remains exactly five verbs in v0.
- `bears-on` is reserved for specimen results bearing on claims.
- Private/restricted non-portable sources may be digest-only only with explicit redaction.
- Public sources still require an excerpt or resolvable pointer.
- No private source excerpt from the supplied packets may be published.

---

### Task 1: Establish the contract surface

**Files:**
- Create: `README.md`
- Create: `grammar/relation-v0.md`
- Create: `laws/no-silent-transitivity.md`
- Create: `laws/visibility-is-not-authority.md`
- Create: `laws/source-road-survives.md`
- Create: `docs/contract-v0.md`
- Create: `schema/free-graph-v0.schema.json`

**Interfaces:**
- Consumes: supplied Free Graph skill contract ancestry.
- Produces: the v0 human and machine-readable contract.

- [x] Extract the five portable verbs and authority boundary without importing skill routing.
- [x] Document repo/non-repo ownership and non-goals.
- [x] Keep local/domain predicates out of the global grammar.

### Task 2: Prove the privacy correction

**Files:**
- Modify: `scripts/fg.py`
- Create: `tests/test_fg.py`
- Modify: `schema/free-graph-v0.schema.json`

**Interfaces:**
- Consumes: `free-graph.packet/v0`.
- Produces: validation that accepts lawful digest-only redaction for private/restricted non-portable sources.

- [x] Write a failing test for a private digest-only redacted source.
- [x] Run it and confirm failure because the validator demanded an excerpt/pointer.
- [x] Implement the minimal validator change.
- [x] Keep public-source excerpt/pointer requirements intact.
- [x] Run the unit tests green.

### Task 3: Publish public-safe specimens

**Files:**
- Create: `specimens/wav-space-v0.public.json`
- Create: `specimens/bandcamp-pressure-v0.public.json`
- Create: `docs/public-specimen-boundary.md`

**Interfaces:**
- Consumes: supplied private-source specimen packets.
- Produces: canonical public-safe packets that validate under v0.

- [x] Remove private excerpts while retaining digests, coordinates, and redaction.
- [x] Normalize domain-local source/claim roles into `extensions`.
- [x] Normalize colloquial non-test `bears-on` edges to `connects`.
- [x] Rehash every transformed record and stamp each packet.
- [x] Validate both specimens.

### Task 4: Add repository gate

**Files:**
- Create: `.github/workflows/validate.yml`
- Modify: `tests/test_fg.py`

**Interfaces:**
- Consumes: validator and public specimens.
- Produces: CI gate for unit tests and specimen validation.

- [x] Add tests that validate both committed specimens.
- [x] Add GitHub Actions job using Python 3.
- [x] Run the full validation contract locally.
