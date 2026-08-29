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
- `evaluation/cases/case_001..006` — 6 minimal synthetic projects, each with one deliberately
  unverified assumption, a `ground_truth.json`, and a `test_*.py` that proves the
  counterexample actually triggers the failure
- `evaluation/evaluate.py` — runs either system over all cases and scores recall
- `docs/CHANGELOG.md` — what was actually measured, iteration by iteration
- `docs/ARCHITECTURE.md` — implemented pipeline + target 5-agent architecture + what was
  considered but not built

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
PYTHONPATH=src python -m assumption_hunter.cli evaluation/cases/case_001_nullable_email
```

See [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md) for the full setup and
evaluation commands.

## Result (see docs/CHANGELOG.md for the full story)

| Metric | Baseline | Advanced V1 |
|---|---:|---:|
| Assumption Detection Rate | 100% (6/6) | 100% (6/6) |

Recall didn't move — both hit the ceiling on this dataset. The interesting
finding is *why*, and it's the project's hot take:

> The bottleneck in agentic code analysis is not generating more findings;
> it is determining which findings are actually supported by evidence — and
> on simple code, even a single-prompt baseline already finds the important
> ones.

## Bottleneck / main failure mode

Both systems over-generate: alongside the one ground-truth assumption per
case, both report several additional true-but-often-irrelevant assumptions
(e.g. "pytest is installed", "the environment has network connectivity").
The Evidence Checker verifies claims against real file content but doesn't
yet rank or suppress low-value-but-true findings — that's the next thing
worth building, not more recall.

## Considered but not implemented

Counterexample Generator, sandboxed Verification Agent, a separate
Assumption Miner stage split out from the Context Analyzer, and multi-agent
debate over borderline evidence classifications. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for why each was deferred.
