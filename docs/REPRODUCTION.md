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

## Approximate runtime and cost (measured 2026-08-31)

- Baseline, 10 cases: ~10 model calls, under 2 minutes total, single-digit
  cents at `gemini-3-flash-preview` pricing.
- Advanced V1, 10 cases: ~50 model calls (1 mining call + ~2-6 evidence
  checks per case), several minutes total, still well under a dollar.

The Vertex AI connection in this environment drops mid-request occasionally
(`RemoteProtocolError`, DNS resolution failures) unrelated to prompt content.
`src/assumption_hunter/llm_client.py` retries each call up to 5 times with
backoff; a full 10-case advanced run typically needs 0-2 retries to complete
cleanly.
