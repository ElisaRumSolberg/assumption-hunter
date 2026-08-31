# Improvement Changelog

Only experiments that were actually run appear here. Ideas that were
discussed but never implemented are in [`ARCHITECTURE.md`](ARCHITECTURE.md)
under "Considered but not implemented."

## Baseline vs. Advanced V1 vs. Advanced V2 — final measured comparison

| Metric | Baseline | Advanced V1 | Advanced V2 | Change (V1→V2) |
|---|---:|---:|---:|---:|
| Assumption Detection Rate (recall, 11 ground-truth items / 10 cases) | 11/11 = 100% | 11/11 = 100% | 11/11 = 100% | 0 |
| Avg. assumptions reported per case | 2.1 | 4.5 | 3.5 | −22% |

Every run used `gemini-3-flash-preview` via Vertex AI, same 10 cases, same
evaluation script (`evaluation/evaluate.py`). Baseline/V1: 2026-08-31.
V2: 2026-08-31 (same day, later pass). Raw output:
[`results/baseline_results.json`](../results/baseline_results.json),
[`results/advanced_results.json`](../results/advanced_results.json) (latest
run reflects V2).

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

## Stage 3 — Advanced V2 (+ severity-aware filtering)

**Tried:** V1's own measured result (above) was that the Evidence Checker
verifies a claim is *true* of the cited file but has no way to reject a
claim that's true and unimportant. V2 acts on that finding directly instead
of just noting it: the Evidence Checker's prompt now also classifies
severity (`high`/`medium`/`low`, with `low` meaning "true but a marginal
environment/toolchain nicety, not a real functional or security risk"), and
`workflow.py` drops `low`-severity findings from the final report on top of
the existing SUPPORTED/PARTIALLY_SUPPORTED filter. The baseline prompt was
also extended to report severity (still a single prompt, no filtering
logic added there) so both systems share the same extended schema
(`{assumption, category, evidence, risk, severity}`).

**Evidence:** recall held at 100% (11/11 — dropping low-severity items
didn't cost a single ground-truth hit, confirming none of the 11 real
assumptions in this dataset were themselves low-severity). Avg. findings
per case dropped from 4.5 (V1) to 3.5 (V2) — a 22% reduction, measured on
the same 10 cases, same script. Baseline's own average also moved slightly
(2.0 → 2.1) because it's now also asked for severity, which nudges its
phrasing/counting marginally; this is noise, not a baseline change.

**Decision:** kept. This is a real, if partial, improvement: V2 closes part
of the gap V1 opened (from 2.25x baseline down to ~1.7x), directly
targeting the exact failure mode the measurement identified, rather than
adding architecture in a direction the data hadn't asked for. It's still
not "solved" — 3.5 vs. 2.1 means the Evidence Checker's severity judgment
is more conservative than a human triager would likely be, and that gap is
worth another iteration if there's time, but isn't in this pass.

## A second, smaller lesson from the trap case

`case_007`'s automated false-positive check (see above) needed a second
look after the V2 run: one candidate's *risk* text read "...shipping labels
and billing **emails** will contain the literal string 'None'..." — about
`User.name` being null, not about the guarded `format_billing_email`'s
null-email handling at all — but the plural "emails" combined with "None"
in the same sentence was enough to trip the trap heuristic
(`required_keywords: ["email"]` + a null/missing term) into a false
"triggered" reading. Manual inspection of the raw candidate confirms V2, like
V1, does not actually re-flag the guarded email path. This wasn't re-tuned
further under time pressure; recorded here instead, because the honest
takeaway generalizes: **automated keyword-based scoring metrics need the
same evidence discipline the pipeline itself is trying to enforce** — a
metric that fires is a hypothesis about the model's output, not a
verified fact about it, until someone reads the raw text.

## Decision: Counterexample Generator

**Not implemented in this pass.** Per the "measure before building" rule,
this was deferred in favor of the severity-filtering work above, because
the measured bottleneck (Evidence Checker over-reporting true-but-low-value
findings) was more directly actionable with the time available. A
counterexample generator would add narrative value for a demo but wasn't
measured against a specific failure mode this pass. See
`docs/ARCHITECTURE.md` for what it would need to prove to be worth adding.

## Hot Take

> The bottleneck in agentic code analysis is not generating more findings —
> it's telling apart the ones that matter from the ones that are merely
> true. A single-prompt baseline already finds the important assumption on
> simple code, every time, with a lean report. A category-driven miner plus
> an evidence-checking stage found the same things but reported 2.25x more
> of them, because "supported by the file" is a much lower bar than "worth
> a developer's attention." Adding a severity filter that acts on that exact
> finding — not more architecture in an unmeasured direction — closed a
> quarter of that gap in about 30 minutes. The lesson generalizes past this
> project: when an agent over-generates, the fix is usually a judgment
> stage, not a bigger pipeline.
