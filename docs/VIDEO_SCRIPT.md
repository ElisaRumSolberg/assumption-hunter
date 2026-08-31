# Solution Video — Voiceover Script (B1 English)

Target length: about 4–5 minutes (hard limit: 5 minutes). Simple B1 English,
spoken by the author. Screen shown alongside each section: `README.md` →
baseline command → advanced command → `docs/CHANGELOG.md` →
`docs/ARCHITECTURE.md` → GitHub repo.

## 0:00–0:30 — Opening / Problem

Hi, I'm Elisa, and this is Assumption Hunter.

Software can look correct and still fail because it uses hidden
assumptions.

For example, a program may assume that every user has an email address,
that an API always returns JSON, or that a config file always exists.

These assumptions can stay hidden until a special case happens.

Assumption Hunter helps find these hidden assumptions before they become
real bugs.

## 0:30–0:55 — What the system does

The system reads a software project and looks for assumptions that may
cause bugs or reliability problems.

For every finding, it shows the assumption, the category, the file with
the evidence, and the possible risk.

The goal is not only to find more things. The goal is to find useful
problems and connect them to clear evidence.

## 0:55–1:25 — Baseline

I started with a simple baseline. The baseline uses one direct prompt. It
does not use tools, retries, or verification.

I run it on the same evaluation case as the advanced version:

```bash
python baseline/baseline.py evaluation/cases/case_007_false_positive_trap
```

In this example, the baseline finds the main problem: the code assumes
that every user has an address. This gives me a simple and fair starting
point.

## 1:25–2:10 — Advanced V1

Now I run the advanced version on the same case:

```bash
python -m assumption_hunter.cli evaluation/cases/case_007_false_positive_trap --format markdown
```

The advanced workflow first analyzes the project and looks for hidden
assumptions. Then the Evidence Checker checks if the findings are really
supported by the project files.

The advanced version finds the same main address assumption. It also finds
more assumptions than the baseline. Some of these findings are correct,
but they are less important for the developer.

## 2:10–2:45 — What I learned and improved

At first, I thought the main problem would be recall, so I expected the
advanced version to find more hidden assumptions.

But the tests showed a different problem. The system could already find
the important assumptions, but it could not tell which findings mattered
most.

So I added a severity level to the Evidence Checker and filtered out
low-severity findings. After I tested the same ten cases again, the
average number of findings per case went down from 4.5 to 3.5. That is
about a 22 percent reduction, with no loss in detection rate.

## 2:45–3:10 — Difficult Case

This case was made as a false-positive trap. It has two similar patterns.
The email case is protected, but the address case is not protected. Both
the baseline and the advanced version avoid reporting the protected email
case as a problem. This shows that the system is not only matching simple
patterns.

## 3:10–3:30 — Tests / Reproducibility

The evaluation projects also have executable tests:

```bash
pytest
```

When I run the test suite, all twelve tests pass. This helps prove that
the evaluation cases work and that another person can run the project
again from a clean environment.

## 3:30–4:00 — Changelog / Iteration Story

Show `docs/CHANGELOG.md`.

I wrote every important step in the Improvement Changelog. I started with
the single-prompt baseline. Then I added structured project analysis.
After that, I added evidence checking. Later, the test results showed that
prioritization was the next problem, so I added severity filtering. I used
the measurements to decide what to build next.

## 4:00–4:25 — Architecture / Scope

Show `docs/ARCHITECTURE.md`.

The current system is still simple on purpose. It has a Context and
Assumption Analyzer, then an Evidence Checker with severity filtering, and
then a structured report. I also thought about adding executable
verification and a counterexample generator. I did not add them because
the data showed that prioritization was more important, so I fixed that
first.

## 4:25–4:50 — Tools Used / Closing

I used Claude Code during this project for parts of the coding work,
including the evidence-checking pipeline and evaluation harness. I also
used ChatGPT for project planning, idea development, reviewing the
hackathon requirements, improving the evaluation plan, and preparing the
video and documentation.

My main lesson is this: the hardest part is not always finding more
problems. It is deciding which findings are really important for the
developer.

The full code and changelog are on GitHub:
https://github.com/ElisaRumSolberg/assumption-hunter

Thank you.
