# Solution Video Script (≤ 5 minutes)

Structure follows the hackathon's required beats. Timings are guidance, not
hard cuts.

## 0:00–0:30 — Problem and simple baseline

- "Software fails less often from syntax errors than from assumptions no one
  checked — every user has an email, an API always returns JSON, a config
  file always exists."
- Show `README.md`: target user (junior devs, engineers inheriting a legacy
  repo), the bottleneck (nobody has a systematic way to surface these before
  production).
- Show the baseline: one prompt, no tools, no retry (`baseline/baseline.py`).

## 0:30–2:00 — End-to-end run

- Run: `PYTHONPATH=src python -m assumption_hunter.cli evaluation/cases/case_007_false_positive_trap --format markdown`
- Narrate case_007 while it runs: one function already guards a missing
  email (`format_billing_email`), a lookalike function doesn't
  (`format_shipping_label`) — this is the hard case built specifically to
  separate real detection from pattern-matching.
- Show the rendered Markdown report (finished, readable — not raw JSON).

## 2:00–3:00 — Comparison, and a metric bug worth admitting

- Show `results/baseline_results.json` vs `results/advanced_results.json`
  for case_007: in the final run, both baseline and advanced correctly avoid
  flagging the guarded email as a risk (0/1 trap rate on both).
- Be honest on camera: an earlier version of the evaluation's own
  false-positive metric had a bug — it matched on generic template words
  ("user", "non-null", "address") instead of the trap's distinguishing word
  ("email"), and briefly reported a false conclusion. Caught by reading the
  raw model output, not by trusting the score. This is in `docs/CHANGELOG.md`
  under its own heading — say so.

## 3:00–4:00 — Evaluation results and changelog

- Show the comparison table from `docs/CHANGELOG.md`.
- Walk through the changelog: recall tied at 100% for both systems (11/11).
  The metric that actually moved: Advanced V1 reports 2.25x more
  assumptions per case (4.5 avg) than baseline (2.0 avg) — the Evidence
  Checker verifies claims are true of the file, not that they're worth a
  developer's attention, so it rejects almost nothing.

## 4:00–4:40 — Main failure mode and hot take

- Failure mode: the Evidence Checker behaves like a rubber stamp, not a
  filter — it classified nearly every candidate SUPPORTED across the
  inspected trajectories. Both systems also over-generate true-but-low-value
  assumptions (Python version requirements, pytest being installed); Advanced
  V1 does this more, not less, because its category-walk actively goes
  looking in six directions per case.
- Hot take: "The bottleneck in agentic code analysis is not generating more
  findings — it's telling apart the ones that matter from the ones that are
  merely true. A single-prompt baseline already finds the important
  assumption every time, with a lean report; more architecture without a
  mechanism to reject true-but-unimportant findings just means more noise
  to read."

## 4:40–5:00 — Close

- One experiment removed: multi-agent debate over borderline evidence
  classifications — discussed, never built, noted honestly in
  `docs/ARCHITECTURE.md` as "considered but not implemented," not listed as
  a removed experiment in the changelog.
- Point to the repo: https://github.com/ElisaRumSolberg/assumption-hunter
