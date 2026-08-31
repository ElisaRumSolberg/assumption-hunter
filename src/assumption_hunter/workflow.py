"""Advanced V2 pipeline: Context+Assumption Analyzer -> Evidence Checker -> Structured Report.

Keeps only SUPPORTED/PARTIALLY_SUPPORTED candidates AND drops "low" severity
ones. V1 kept every evidence-backed candidate regardless of how much a
developer should actually care, which measurably produced 2.25x more
findings per case than the baseline with no gain in what mattered (see
docs/CHANGELOG.md). V2 adds severity as a second filter, on top of (not
instead of) the evidence check, so the report uses the same
{"assumptions": [{assumption, category, evidence, risk, severity}]} schema
as the baseline (which now also reports severity, per its own single-prompt
judgment).
"""

from assumption_hunter.agents import context_analyzer, evidence_checker

KEPT_STATUSES = {"SUPPORTED", "PARTIALLY_SUPPORTED"}
DROPPED_SEVERITIES = {"low"}

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def analyze_project_verbose(project_path: str) -> dict:
    candidates = context_analyzer.analyze(project_path)
    checked = evidence_checker.check_all(project_path, candidates)
    kept = [
        c
        for c in checked
        if c.get("status") in KEPT_STATUSES and c.get("severity", "medium") not in DROPPED_SEVERITIES
    ]
    kept.sort(key=lambda c: _SEVERITY_ORDER.get(c.get("severity", "medium"), 1))
    assumptions = [
        {
            "assumption": c["assumption"],
            "category": c["category"],
            "evidence": c["evidence"],
            "risk": c["risk"],
            "severity": c.get("severity", "medium"),
        }
        for c in kept
    ]
    return {"assumptions": assumptions, "all_candidates": checked}


def analyze_project(project_path: str) -> dict:
    result = analyze_project_verbose(project_path)
    return {"assumptions": result["assumptions"]}
