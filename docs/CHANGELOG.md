# Improvement Changelog

Only experiments that were actually run appear here. Ideas that were
discussed but never implemented are in [`ARCHITECTURE.md`](ARCHITECTURE.md)
under "Considered but not implemented."

## Baseline vs. Advanced V1 — final measured comparison

| Metric | Baseline | Advanced V1 | Change |
|---|---:|---:|---:|
| Assumption Detection Rate (recall, 11 ground-truth items / 10 cases) | 11/11 = 100% | 11/11 = 100% | 0 |
| False-positive trap rate (case_007, guarded assumption) | 0/1 = 0% | 0/1 = 0% | 0 |
| Avg. assumptions reported per case | 2.0 | 4.5 | +2.25x |

Both runs used `gemini-3-flash-preview` via Vertex AI, same 10 cases, same
evaluation script (`evaluation/evaluate.py`), 2026-08-31. Raw output:
[`results/baseline_results.json`](../results/baseline_results.json),
[`results/advanced_results.json`](../results/advanced_results.json).

## Stage 1 — Baseline (single prompt)

**Tried:** one prompt, full project text, JSON-only response. No tools, no
retry, no code execution — the floor every later stage is measured against.

**Evidence:** 100% recall across all 10 cases, including case_010 (two
independent assumptions in one file) and case_008 (a security/silent-failure
assumption, not a crash). Reports a lean 2.0 assumptions/case on average.

**Decision:** kept as the comparison floor. This is the project's central,
slightly uncomfortable finding — see Hot Take.

## Stage 2 — Advanced V1 (Context+Assumption Analyzer → Evidence Checker)

**Tried:** added a first stage that explicitly walks 6 fixed assumption
categories (data, environment, api, time, business_rule, auth) and requests
one evidence file per candidate, then a second stage that re-reads the
*actual* file from disk (not the LLM's memory of it) and classifies each
candidate as SUPPORTED / PARTIALLY_SUPPORTED / UNVERIFIED / CONTRADICTED.
Only SUPPORTED and PARTIALLY_SUPPORTED candidates reach the final report.

**Evidence:** recall unchanged (100%, tied with baseline — expected, since
baseline already found every ground-truth assumption). The category-walk
more than doubled the candidates generated per case (4.5 avg vs. 2.0). The
Evidence Checker did not meaningfully cut that back down: across the runs
inspected in detail (`trajectories/case_001_trajectory.json`,
`trajectories/case_007_trajectory.json`), it classified nearly every
candidate SUPPORTED or PARTIALLY_SUPPORTED and rejected almost nothing.

**Decision:** kept the architecture (evidence-linking against real file
content instead of model memory is a real reliability property worth
having), but **do not claim it reduced noise or improved precision on this
dataset — it didn't measurably**. The Evidence Checker behaves more like a
rubber stamp than a filter here: it verifies a claim is *true* of the cited
file, but a candidate can be true and still be low-value (e.g. "the
environment has network connectivity"), and the current prompt has no
mechanism to reject on those grounds.

## A false start worth reporting: the trap-detection metric had a bug

`case_007` (false-positive trap) was built specifically to test whether a
system distinguishes a real assumption from a lookalike that's already
guarded in the code. On an early run, `evaluation/metrics.py`'s trap check
used the same lenient keyword-overlap logic as the recall metric, and it
flagged **both** baseline and advanced as "triggering the trap" — but
inspecting the raw output showed neither system had actually mentioned
`email` at all. The match fired on generic template words the trap sentence
shared with the real ground-truth sentence ("user", "non-null", "address"),
not on the thing that actually made it a trap.

**Fix:** trap matching now requires the trap's distinguishing keyword(s)
(`required_keywords`, e.g. `"email"`) plus a null/missing-related term
(`required_any_of_keywords`) to actually be present in the detected text,
instead of a generic overlap ratio. After the fix, both systems correctly
score 0/1 on the trap in the final run — a real (if less dramatic) result:
neither system pattern-matched into the trap on this case.

**Learning:** the same brittleness (plural/synonym mismatches, e.g.
"datetimes" vs "datetime") was independently causing false *negatives* in
recall scoring for `case_005` on one run. Fixed with light singularization
and snake_case splitting in `_keywords()`. This is a direct instance of the
rubric's own instruction: connect every claim to evidence, and check the
raw output before trusting an automated score — the evaluation script is
part of the system under test, not ground truth.

## Decision: Counterexample Generator (V2)

**Not implemented in this pass.** Per the "measure before building" rule,
V2 was deferred because the measured bottleneck (see above) is not recall —
it's that the Evidence Checker doesn't discriminate between "true and
important" and "true but low-value" candidates, so Advanced V1 reports
2.25x more findings than baseline without a corresponding gain in what the
user actually needs to act on. A counterexample generator would add
narrative value for a demo but wasn't measured against this specific
failure mode, so it isn't listed as a completed experiment. See
`docs/ARCHITECTURE.md` for what it would need to prove to be worth adding.

## Hot Take

> The bottleneck in agentic code analysis is not generating more findings —
> it's telling apart the ones that matter from the ones that are merely
> true. On simple, single-file code, even a single-prompt baseline already
> finds the important assumption, every time, with a lean report. A
> category-driven miner plus an evidence-checking stage found the same
> things but reported 2.25x more of them, because "supported by the file"
> is a much lower bar than "worth a developer's attention." Where agentic
> architecture should earn its cost is in that second, harder judgment —
> not in raising recall that was already at ceiling.
