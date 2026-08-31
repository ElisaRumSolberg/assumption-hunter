# Assumption Hunter

> Find the assumptions your software doesn't know it's making.

An agentic tool that reads a software project (code, README, config, tests)
and reports the hidden, unverified assumptions it relies on — each tied to
the file that makes it and the risk if it's false.

## Target user

Junior developers, engineers inheriting a legacy repo, and small teams
reviewing an unfamiliar codebase before it breaks in production.

## What's here

- `baseline/baseline.py` — single-prompt baseline (no tools, no retry, no code execution)
- `src/assumption_hunter/` — Advanced pipeline: Context+Assumption Analyzer → Evidence Checker
  (V2 adds severity classification + low-severity filtering)
- `evaluation/cases/case_001..010` — 10 minimal synthetic projects (11 ground-truth assumptions),
  including one with two independent assumptions in one file (`case_010`) and one deliberate
  false-positive trap where a lookalike function is already guarded (`case_007`). Every case has
  a `ground_truth.json` and a `test_*.py` that proves its counterexample actually triggers the
  failure.
- `evaluation/evaluate.py` — runs either system over all cases and scores recall + false-positive rate
- `docs/CHANGELOG.md` — what was actually measured, iteration by iteration, including a
  measurement bug that was found and fixed mid-project
- `docs/ARCHITECTURE.md` — implemented pipeline + target 5-agent architecture + what was
  considered but not built
- `docs/VIDEO_SCRIPT.md` — outline for the solution video
- `trajectories/` — one trajectory per case (baseline + both advanced stages), all 10 cases

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
PYTHONPATH=src python -m assumption_hunter.cli evaluation/cases/case_001_nullable_email --format markdown
```

See [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) for the full setup and
evaluation commands.

## Result (see docs/CHANGELOG.md for the full story)

| Metric | Baseline | Advanced V1 | Advanced V2 |
|---|---:|---:|---:|
| Assumption Detection Rate (recall) | 100% (11/11) | 100% (11/11) | 100% (11/11) |
| Avg. assumptions reported per case | 2.1 | 4.5 | 3.5 |

Recall never moved — all three hit the ceiling on this dataset. What moved
is the noise level: V1's Evidence Checker verified that a claim is true of
the cited file but had no way to reject a claim that's true and
unimportant, so it reported 2.25x more findings per case than baseline. V2
acts on that measured finding directly — it also classifies severity and
drops low-severity findings — and cut the average by 22% (4.5 → 3.5)
without losing a single ground-truth hit. That's the project's hot take:

> The bottleneck in agentic code analysis is not generating more findings —
> it's telling apart the ones that matter from the ones that are merely
> true. A single-prompt baseline already finds the important assumption on
> simple code, every time. Adding a severity filter that acts on a measured
> finding — not more architecture in an unmeasured direction — closed a
> quarter of the noise gap in about 30 minutes.

## Bottleneck / main failure mode

V1's Evidence Checker classified almost every candidate SUPPORTED or
PARTIALLY_SUPPORTED and rejected almost nothing — it behaved like a rubber
stamp, not a filter. V2's severity classification closes part of this (V1
4.5 → V2 3.5 avg/case) but not all of it: 3.5 is still ~1.7x baseline's 2.1,
so the Evidence Checker's severity judgment is more conservative than a
human triager would likely be. Both systems also still surface some
true-but-marginal assumptions alongside the real risk (e.g. "pytest is
installed", "the interpreter is a specific version") — ranking these out
entirely, rather than just filtering "low," is the next thing worth
building, not more recall.

The project also surfaced a methodology bug worth naming: an early version
of the evaluation script's own trap-detection metric had a false-positive
problem of its own (matching on generic template words instead of the
distinguishing term), which briefly produced a wrong conclusion until the
raw model output was inspected directly. See `docs/CHANGELOG.md`.

## Considered but not implemented

Counterexample Generator, sandboxed Verification Agent, a separate
Assumption Miner stage split out from the Context Analyzer, and multi-agent
debate over borderline evidence classifications. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for why each was deferred.
