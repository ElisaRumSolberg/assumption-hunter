# Architecture

## Implemented

```
Repository
    |
    v
Context + Assumption Analyzer   (src/assumption_hunter/agents/context_analyzer.py)
    |  candidate assumptions, one evidence file path each
    v
Evidence Checker                (src/assumption_hunter/agents/evidence_checker.py)
    |  re-reads the cited file from disk, classifies SUPPORTED/PARTIALLY_SUPPORTED/
    |  UNVERIFIED/CONTRADICTED, drops the last two
    v
Structured Report               ({"assumptions": [{assumption, category, evidence, risk}]})
```

`src/assumption_hunter/workflow.py` wires these two stages together as
`analyze_project(project_path)`, returning the same JSON schema the baseline
returns, so `evaluation/evaluate.py` can score both with one script.

The baseline (`baseline/baseline.py`) is intentionally a single prompt over
the same file-reading tool (`tools/file_reader.py`) with no tool calls, no
retry loop, and no code execution — it exists only as the comparison floor,
per the project's hard rule that baseline and advanced must share an output
schema and both be measured on the same cases.

## Target architecture (not yet built)

```
Repository
    |
    v
Context Analyzer          -- stack, structure, domain rules, test/config locations
    |
    v
Assumption Miner           -- category-driven candidate generation (currently merged into Context Analyzer above)
    |
    v
Evidence Checker           -- SUPPORTED/PARTIALLY_SUPPORTED/UNVERIFIED/CONTRADICTED (built)
    |
    v
Counterexample Generator   -- turns an assumption into a concrete failing input
    |
    v
Verification Agent         -- writes a small test, runs it sandboxed, rejects false positives
    |
    v
Final Risk Report
```

Splitting "Context Analyzer" and "Assumption Miner" into two separate LLM
calls was in the target design but not built in this pass — V1 merges them
into one call (see `docs/CHANGELOG.md`) because the two-stage version was
what got measured within the time budget.

## Considered but not implemented

- **Counterexample Generator.** Would take a SUPPORTED assumption and produce
  a concrete failing input (e.g. `User(email=None)`), matching what the
  evaluation cases already hand-author in `test_*.py`. Deferred because the
  measured bottleneck in this pass (see CHANGELOG) is over-generation of
  true-but-low-value assumptions, not a lack of concrete counterexamples for
  the assumptions already found. Worth building if a future evaluation round
  shows verified findings materially reduce false positives.
- **Verification Agent (sandboxed test runner).** Planned to run
  `subprocess.run(cmd, timeout=10, cwd=sandbox_dir)` with network off and no
  destructive commands allowed, generating and executing a small pytest file
  per counterexample. Not implemented because it depends on the
  Counterexample Generator above.
- **Multi-agent debate.** Discussed as a way to have two model calls argue
  over a borderline SUPPORTED/UNVERIFIED classification before accepting it.
  Never implemented or run — it is not a removed experiment, it was never
  tried, so it does not appear in `CHANGELOG.md`.
- **Separate Assumption Miner stage** (category-driven mining as its own LLM
  call, distinct from Context Analyzer). Discussed as the "true" 5-agent
  target architecture; not split out because the merged V1 call already
  reaches ceiling recall on the current evaluation set, so there was nothing
  measured that the split would have fixed.
