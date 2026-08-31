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
- `src/assumption_hunter/` — Advanced V1 pipeline: Context+Assumption Analyzer → Evidence Checker
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

| Metric | Baseline | Advanced V1 | Change |
|---|---:|---:|---:|
| Assumption Detection Rate (recall) | 100% (11/11) | 100% (11/11) | 0 |
| False-positive trap rate | 0% (0/1) | 0% (0/1) | 0 |
| Avg. assumptions reported per case | 2.0 | 4.5 | +2.25x |

Recall didn't move — both hit the ceiling on this dataset, and both
correctly passed the false-positive trap case. What *did* move is the noise
level: Advanced V1 reports 2.25x more assumptions per case than the
baseline, because its Evidence Checker verifies that a claim is true of the
cited file but has no mechanism to reject a claim that's true and
unimportant. That's the project's hot take:

> The bottleneck in agentic code analysis is not generating more findings —
> it's telling apart the ones that matter from the ones that are merely
> true. A category-driven miner plus an evidence-checking stage found the
> same things a single-prompt baseline did, but reported more than twice as
> many, because "supported by the file" is a much lower bar than "worth a
> developer's attention."

## Bottleneck / main failure mode

The Evidence Checker classifies almost every candidate SUPPORTED or
PARTIALLY_SUPPORTED and rejects almost nothing (see
`trajectories/case_001_trajectory.json` and
`trajectories/case_007_trajectory.json`) — it behaves like a rubric stamp,
not a filter. Both systems also over-generate true-but-often-irrelevant
assumptions alongside the real risk (e.g. "pytest is installed", "the
environment has network connectivity"); Advanced V1 does this *more*, not
less, because its category-walk actively goes looking in six directions per
case. Ranking or suppressing low-value-but-true findings is the next thing
worth building, not more recall.

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
