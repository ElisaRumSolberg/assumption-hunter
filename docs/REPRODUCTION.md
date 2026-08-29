# Reproduction Guide

## Versions used

- Python 3.11.9
- `google-genai` (Vertex AI mode)
- Model: `gemini-3-flash-preview`
- GCP project/location come from `.env` (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global`)

## Setup

```bash
git clone <repository>
cd assumption-hunter
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env        # fill in GOOGLE_CLOUD_PROJECT
gcloud auth application-default login
```

Vertex AI auth is via `gcloud` application-default credentials, not an API
key — the `google-genai` client is constructed with `vertexai=True` and reads
project/location from `.env`.

## Run the baseline on one case

```bash
python baseline/baseline.py evaluation/cases/case_001_nullable_email
```

## Run the advanced pipeline (CLI)

```bash
PYTHONPATH=src python -m assumption_hunter.cli evaluation/cases/case_001_nullable_email
```

## Run the full evaluation (both systems, all cases)

```bash
python evaluation/evaluate.py baseline
python evaluation/evaluate.py advanced
```

Each run prints a per-case recall line and an overall recall summary, and
writes `results/baseline_results.json` / `results/advanced_results.json`
(overwritten on each run — copy them out first if you want to diff two runs).

## Verify a case's counterexample independently

```bash
cd evaluation/cases/case_001_nullable_email
python -m pytest -q
```

Each case's `test_*.py` uses `pytest.raises(...)` to prove the counterexample
in its `ground_truth.json` actually reproduces the stated failure.

## Approximate runtime and cost (measured 2026-08-30)

- Baseline, 6 cases: ~6 model calls, under 1 minute total, single-digit cents
  at `gemini-3-flash-preview` pricing.
- Advanced V1, 6 cases: ~12 model calls (1 mining call + up to ~4-6 evidence
  checks per case), a few minutes total (network-bound; one run hit a
  transient DNS/connection error mid-batch and needed a retry), still
  single-digit cents.
