"""Advanced V1 pipeline: Context+Assumption Analyzer -> Evidence Checker -> Structured Report.

Keeps only SUPPORTED and PARTIALLY_SUPPORTED candidates so the final report
uses the same {"assumptions": [{assumption, category, evidence, risk}]} schema
as the baseline.
"""

from assumption_hunter.agents import context_analyzer, evidence_checker

KEPT_STATUSES = {"SUPPORTED", "PARTIALLY_SUPPORTED"}


def analyze_project_verbose(project_path: str) -> dict:
    candidates = context_analyzer.analyze(project_path)
    checked = evidence_checker.check_all(project_path, candidates)
    kept = [c for c in checked if c.get("status") in KEPT_STATUSES]
    assumptions = [
        {
            "assumption": c["assumption"],
            "category": c["category"],
            "evidence": c["evidence"],
            "risk": c["risk"],
        }
        for c in kept
    ]
    return {"assumptions": assumptions, "all_candidates": checked}


def analyze_project(project_path: str) -> dict:
    result = analyze_project_verbose(project_path)
    return {"assumptions": result["assumptions"]}
