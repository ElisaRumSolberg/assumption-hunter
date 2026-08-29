# Improvement Changelog

Only experiments that were actually run appear here. Ideas that were discussed
but never implemented are in [`ARCHITECTURE.md`](ARCHITECTURE.md) under
"Considered but not implemented."

## Baseline vs. Advanced V1

| Metric | Baseline | Advanced V1 |
|---|---:|---:|
| Assumption Detection Rate (recall) | 6/6 = 100% | 6/6 = 100% |
| Avg. assumptions reported per case | 3.0 | 4.2 |
| Evidence-checker rejection rate | n/a | 0% (0 of 25 candidates rejected) |

Both runs used `gemini-3-flash-preview` via Vertex AI, on the same 6 cases,
same day. Raw output: [`results/baseline_results.json`](../results/baseline_results.json),
[`results/advanced_results.json`](../results/advanced_results.json).

## Stage 1 — Baseline (single prompt)

**Experiment:** one prompt, full project text, JSON-only response. No tools,
no retry, no code execution.

**Result:** 100% recall on all 6 cases. The model reliably names the one
ground-truth assumption per case, plus 1-3 additional true (but out-of-scope)
assumptions it notices in the same file (e.g. "pool_size=5 is hardcoded",
"catalog items always have a 'name' key").

**Decision:** keep as the comparison floor. It is a strong floor — this is
the main finding of this project, see the Hot Take below.

## Stage 2 — Advanced V1 (Context+Assumption Analyzer → Evidence Checker)

**Experiment:** added a first stage that explicitly walks 6 fixed assumption
categories (data, environment, api, time, business_rule, auth) and requests
one evidence file per candidate, then a second stage that re-reads the
*actual* file from disk (not the LLM's memory of it) and classifies each
candidate as SUPPORTED / PARTIALLY_SUPPORTED / UNVERIFIED / CONTRADICTED.
Only SUPPORTED and PARTIALLY_SUPPORTED candidates reach the final report.

**Result:** recall unchanged (100%, same as baseline — expected, since
baseline already found the ground-truth assumption in every case). The
category-walk produced more candidates per case (4.2 avg vs. 3.0 for
baseline). The evidence checker rejected 0 of 25 candidates: every generated
assumption on these small, single-file cases was in fact true of the file it
cited, so there was nothing to reject.

**Decision:** keep the architecture (evidence linking against real file
content, not model memory, is a meaningful reliability property even when it
doesn't change the score here), but **do not claim it improved detection or
precision on this dataset** — it didn't, and the changelog rule is to report
what was actually measured. The real bottleneck this run exposed is the
**evaluation set**, not the pipeline: see Hot Take.

## Why recall didn't move — a measurement caveat, not a pipeline result

The 6 cases were each built as one minimal file with exactly one intended
hidden assumption, per the "kalıp" (case_001 pattern). `gemini-3-flash-preview`
finds these single, syntactically obvious assumptions (e.g. `user.email.lower()`
with no null check) reliably in one shot — there is a hard ceiling at 100%
recall that neither architecture change nor more agents can move on this
dataset. This is itself evidence for the hot take below: on simple code, the
bottleneck was never *finding* the assumption.

## Decision: Counterexample Generator (V2)

**Not implemented in this pass.** Per the "measure before building" rule,
V2 was deferred because the current bottleneck (per the evidence above) is
not recall — it's distinguishing real risks from the extra, sometimes
speculative assumptions both systems already over-generate (e.g. "the
environment has network connectivity", "pytest is installed"). A
counterexample generator adds narrative value for a demo but wasn't measured
against this failure mode, so it isn't listed as a completed experiment.
See `ARCHITECTURE.md` for what it would need to prove to be worth adding.

## Hot Take

> The bottleneck in agentic code analysis is not generating more findings;
> it is determining which findings are actually supported by evidence — and
> on simple, single-file code, even a single-prompt baseline already finds
> the important ones. Where agentic architecture should earn its cost is in
> separating the real risk from the pile of technically-true-but-irrelevant
> assumptions both systems generate (Python version requirements, pytest
> being installed, network connectivity existing) — not in raising recall
> that is already at ceiling.
