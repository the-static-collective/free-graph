# REASON-SPACE-002 — Choose the next investigation from the graph

This extends [REASON-SPACE-001](../REASON-SPACE-001.md), preserving the **existing Free Graph v0 five-verb grammar and content-addressed record identities**. It addresses the specific recurring problem: the same question is investigated repeatedly even though previous experiments already recorded their failures and partial observations.

## The mechanism

The generic `scripts/inquiry_selector.py` calls the *source-owned Free Graph* `pressure(packet)` first, rather than assuming a fixed ALEX → planZ → Dogram → GRAFT workflow.

It observes:

- Which hypotheses are unresolved or proposed.
- How many original test edges are actually recorded.
- Which attributed evidence bearings support, refuse or leave each unresolved.
- Which **instrument profile IDs are explicitly recorded** on prior probe nodes (not inferred from a plausible label).
- A bounded **task cut supplied by the human**, listing the exact tools relevant to this question, whether a new source scope exists, whether an original positive specimen is available, and whether imagination/alternative-hypothesis work is wanted.

The selector returns a **proposal**, not an execution. Its finite registry, `research/reason-space-002/instruments.json`, preserves each tool's owner, original source, nature of work, preconditions and limitations. The registry does not grant network access, code execution, identity access, source-owner adoption, or artifact delivery.

The first control runs against an actual previously completed MOTIF source-pinned investigation, so it sees historical executed probes by ALEX, planZ, Dogram, and GRAFT; it does **not** call any of them again. The previous report still has **2 recorded refusals, 3 unresolved findings, 0 supports**, with no authentic PlayDeck performance witness.

The experiment compares four **explicit task cuts** on that *same* historical source:

| Human-declared context | Result | Limitation |
| --- | --- | --- |
| No new public source and no original positive receipt | **HOLD / no tool selected** | Prior investigation can't become new evidence through repetition |
| Human declares an actually new bounded source scope | **propose GRAFT public source inspection** | Needs an independently checked scope and permission before live GitHub calls |
| Human declares a genuine original positive performance receipt | **propose original PlayDeck validation** | Existence, ownership and validity not demonstrated by the declaration |
| Human says no further inquiry required | **no investigation** | Saves unnecessary work and attention |

The result includes the previous instrument IDs so later tools can recognize which kind of investigation has **already been attempted**. Merely using a different filename or lens does not create a fresh physical observation.

## Does LSD help? YES — but in a different register

[LSD's historical design in The Daily Slice](https://github.com/the-static-collective/the-daily-slice/blob/23c3d4bf7e4febb89919a3d54b6e8aaf3a764120/slices/2026/08/2026-08-24/reality-bakers.md) describes it as a **reversible possibility-space and constraint-relaxation organ**: open an alternative frame, generate structural candidates, **RETURN** to the original constraints, and leave a **RECEIPT**. It belongs **upstream of** empirical testing and source-owner admission, *not* as a substitute for evidence.

LSD is therefore a candidate **divergence profile**, represented under `lsd-divergence`. The selector can show a *human-only ideation invitation* if the person expressly requests it. Any newly imagined hypothesis remains proposed and requires independent testing. LSD does not resolve the historical no-support gap, grant authority or count as a previously executed verified operation.

**GitHub reality:** During this investigation, a repository specifically named `the-static-collective/LSD` was **not available to the connected GitHub tools** (404), and no independently verifiable source-owned LSD runtime was discovered in the Collective's accessible repository inventory. Historical material also describes LSD as a skill/reasoning profile rather than necessarily a separate executable GitHub project. The selector intentionally marks its owner `UNVERIFIED_EXECUTABLE_REPO`, its mode `HUMAN_REVIEWED_IDEATION_PROFILE_ONLY`, and availability `NOT_CONNECTED_AS_SOURCE_OWNED_EXECUTABLE`. We have **not** falsely wired or executed unknown LSD code.

This is a particularly good place for LSD: use it when the reasoner is prematurely locked into one hypothesis and could benefit from trying alternate framings, **but do not force it when a single well-defined empirical check is sufficient**.

## Technical details

- `scripts/reason_space.py` accepts an **optional explicit `instrument` on probe events**, embedded only in a node's `extensions.instrument`. This is a backward-compatible extension, not a new graph verb. Only allowlisted instrument IDs are valid.
- `scripts/motif_reason_bridge.py` now stamps the four **actually executed** historical tool probes from the original frozen MOTIF MAP-002 report. PlayDeck is intentionally **not** marked as executed: only its source contracts were inspected.
- `scripts/inquiry_selector.py` selects a bounded follow-up from typed `free-graph.inquiry-task-cut/v0`; it explicitly refuses extra fields or permission flags and does not interpret repetition as independent evidence.
- `scripts/select_motif_next.py` is a local, no-network demonstration CLI that replays an **exact Git-blob-pinned MOTIF historical receipt**, with scope flags that are human declarations and *not* claims that the indicated witnesses really exist.
- `tests/test_inquiry_selector.py` adds synthetic adversarial controls for stale/repeated attempts, competing evidence, consent, untrusted registries, no-action choice and LSD staying speculative.

The CI run **#42127881159** checked out an exact original public MOTIF Git report and an original public Daily Slice description of LSD, verified their Git blobs, ran **69 Free Graph tests**, and executed four bounded selection controls. All succeeded. The four JSON results are stored in the run's artifact.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/select_motif_next.py <exact-original-MOTIF-002-report.json> --ideation
```

## Strongest limit

This is a **deterministic, graph-native recommendation engine** over a controlled evidence cut. It is *not* general semantic understanding, learned tool-selection weights, measured value-of-information, an actual LSD program execution, a live internet agent, or a source-owner admission. Selection is not execution, and human-declared existence of a new source or witness is not independent evidence that one exists.

The next falsifiable experiment would compare this selector against a fixed-tool sequence and a naive always-search baseline on **held-out Free Graph reasoning trails**, measuring unnecessary repeated inquiries, missed useful probes, permission mistakes and actual resource consumption.
