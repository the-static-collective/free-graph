# Promotion/Invariance Crucible v0 Implementation Plan

> **Execution note:** implement inline with test-driven development; expand beyond the founding two repositories only by harvesting pre-existing unrelated artifacts, not by constructing clause-specific witnesses.

**Goal:** Build a deterministic clause-level harness that detects vocabulary leakage, consumes native unrelated-system receipts, and derives a `split-required` result without widening Free Graph's substrate contract or accepting verdict ground truth as input.

**Architecture:** A JSON case contains native consumer metadata and normalized operational traces. A dependency-free Python evaluator checks behavior, material difference, mandatory poison attacks, clause-level translation evidence, and missing discriminators. National Treasure remains an independent repository and is pinned by immutable commit and native receipt digest.

**Tech stack:** Python 3 standard library, `unittest`, JSON, existing Free Graph validator/CI.

**Spec:** `docs/superpowers/specs/2026-08-24-promotion-crucible-v0-design.md`

## Global constraints

- Do not change `free-graph.packet/v0` or the five-verb grammar.
- Do not add runtime infrastructure, connectors, databases, or services.
- Decide clauses from operational traces, never declaration fields.
- Require a separate attributable gate for warrant rise or consequential state change.
- Permit gate-mediated causal participation by a projection.
- Count only materially different positive embodiments toward portability.
- Report poison outcomes separately; they never count as positive embodiments.
- Emit no average, percentage, or aggregate green.
- Preserve a lawfully derived `split-required` as a successful v0 result.
- Search pre-existing unrelated systems before constructing clause-specific specimens.

---

### Task 1: Lock the evaluator contract with failing tests

**Files:**

- Create: `tests/test_promotion_crucible.py`
- Create: `specimens/promotion-crucible-v0/case.json`

- [ ] Write tests for the five operational clause checks.
- [ ] Write paired consequence tests: ungated state change refuses; separately attributable gate-mediated state change passes.
- [ ] Write decoder-history and lens/object identity negative controls.
- [ ] Write a fake second wrapper test proving implementation reuse cannot satisfy material difference.
- [ ] Write the mandatory copied-vocabulary/reversed-behavior poison test.
- [x] Write an end-to-end behavior-derived verdict test with no score and whole `split-required`.
- [x] Reject expected/verdict ground-truth keys anywhere in the case input.
- [x] Mutate behavior to prove the same clause can derive `supports`, `only-one-domain`, and `refuses`.
- [ ] Run `python3 -m unittest tests.test_promotion_crucible -v` and verify RED because the evaluator does not exist.

### Task 2: Implement the smallest behavior-first evaluator

**Files:**

- Create: `scripts/promotion_crucible.py`

- [ ] Validate the harness-local case schema and unique IDs.
- [ ] Evaluate operational traces for each clause without consulting self-description.
- [ ] Enforce separately attributable gate receipts for warrant rise and state change.
- [ ] Enforce append-only history and view-versus-object identity.
- [ ] Group independent positive supports by material-embodiment key.
- [ ] Evaluate mandatory attacks separately.
- [ ] Derive clause verdicts, missing discriminators, and whole verdict by conjunction.
- [ ] Emit a canonical case digest and deterministic JSON.
- [ ] Run the focused suite and verify GREEN.

### Task 3: Pin and adapt the independent SSW receipt

**Files:**

- Create: `specimens/promotion-crucible-v0/national-treasure-ssw-math-001.receipt.json`
- Update: `specimens/promotion-crucible-v0/case.json`
- Update: `tests/test_promotion_crucible.py`

- [ ] Copy the native receipt bytes from National Treasure remote commit `65e67062a3be933332db36af8bc095fc9b2660b4` without editing its schema or vocabulary.
- [ ] Record its SHA-256 and immutable source path in the crucible case.
- [ ] Test the adapter's epistemic and identity readings against native fields.
- [ ] Prove the native receipt contains none of the Free Graph constitutional vocabulary used by the local fixture.

### Task 4: Emit the deterministic receipt and human interpretation

**Files:**

- Create: `specimens/promotion-crucible-v0/receipt.json`
- Create: `docs/promotion-crucible-v0.md`

- [ ] Generate the receipt twice and confirm byte identity.
- [ ] Document every clause verdict, poison outcome, semantic fracture, and missing discriminator.
- [ ] State the consequence clause exactly: no consequence without a separately attributable local gate.
- [x] State that `split-required` is the observed successful discovery, not fixture ground truth.

### Task 4A: Harvest pre-existing unrelated systems

**Files:**

- Add unedited native Full Bowl receipts under `specimens/promotion-crucible-v0/`.
- Update the case, evaluator adapters, tests, receipt, and interpretation.

- [x] Evaluate Full Bowl 001 as-is and preserve its unresolved authority/consequence result.
- [x] Evaluate Full Bowl 002's native ordered owner-local phases as independent authority evidence while preserving `FB001-U001` as an unresolved consequence boundary.
- [x] Search Haunted Toaster's existing replay/archive behavior for history without inventing a new paired-rendering specimen.
- [x] Keep consequence and history `only-one-domain` because their required native discriminators were not found.

### Task 5: Repository verification and draft publication

**Files:** verify all additions above without unrelated changes.

- [ ] Run `python3 -m unittest discover -s tests -v`.
- [ ] Validate both existing public Free Graph specimens.
- [ ] Run the crucible CLI over the committed case and compare against the committed receipt.
- [ ] Run `git diff --check` and inspect the complete diff.
- [ ] Commit by intent, push the feature branch, and open a draft PR closing issue #5 while referencing Free Graph #2 and National Treasure #36.
- [ ] Do not merge without explicit per-PR landing approval.
