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

## 2:00–3:00 — Baseline vs. Advanced side by side, and the real failure mode

- Run `python baseline/baseline.py evaluation/cases/case_007_false_positive_trap`
  right after the advanced run above: baseline finds 1 clean finding
  (`address`), advanced finds several more, evidence-backed but not equally
  important. Say it plainly on camera: "The advanced pipeline finds the same
  core assumption, plus more evidence-backed but lower-priority ones. Both
  correctly avoid the guarded-email false positive. This revealed the real
  bottleneck: not recall, it's prioritization."
- Mention, briefly, the honesty story in `docs/CHANGELOG.md`: an earlier
  version of the evaluation's own trap-detection metric had two separate
  false-trigger bugs during this project (matching on generic template
  words, then a coincidental "emails" mention in an unrelated sentence) —
  caught both times by reading raw model output, not by trusting the score.

## 3:00–4:00 — Evaluation results and the changelog's closed loop

- Show the comparison table from `docs/CHANGELOG.md`: recall tied at 100%
  across baseline/V1/V2 (11/11). Avg. findings per case: baseline 2.1 → V1
  4.5 → **V2 3.5**.
- Say what V2 actually is: "Instead of just writing down 'the Evidence
  Checker doesn't discriminate on importance' as a limitation, I closed part
  of that loop — added severity classification to the Evidence Checker,
  filtered out low-severity findings, re-measured. 22% fewer findings per
  case, zero recall lost."

## 4:00–4:40 — Main failure mode and hot take

- Failure mode: V2 helps but doesn't fully close the gap — 3.5 is still
  ~1.7x baseline's 2.1, so the severity filter is more conservative than a
  human triager would be. That's the honest state of the project, not a
  solved problem.
- Hot take: "The bottleneck in agentic code analysis is not generating more
  findings — it's telling apart the ones that matter from the ones that are
  merely true. A single-prompt baseline already finds the important
  assumption on simple code, every time. Adding a severity filter that acts
  on a measured finding — not more architecture in an unmeasured direction —
  closed a quarter of that noise gap in about 30 minutes."

## 4:40–5:00 — Close

- One experiment removed: multi-agent debate over borderline evidence
  classifications — discussed, never built, noted honestly in
  `docs/ARCHITECTURE.md` as "considered but not implemented," not listed as
  a removed experiment in the changelog.
- Point to the repo: https://github.com/ElisaRumSolberg/assumption-hunter
