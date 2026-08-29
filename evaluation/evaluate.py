"""Run a system (baseline or advanced) over all evaluation cases and score recall.

Usage:
    python evaluation/evaluate.py baseline
    python evaluation/evaluate.py advanced
"""

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from evaluation.metrics import compute_recall

CASES_DIR = REPO_ROOT / "evaluation" / "cases"
RESULTS_DIR = REPO_ROOT / "results"


def load_cases() -> list[dict]:
    cases = []
    for case_dir in sorted(CASES_DIR.iterdir()):
        gt_path = case_dir / "ground_truth.json"
        if gt_path.exists():
            cases.append(json.loads(gt_path.read_text(encoding="utf-8")))
    return cases


def get_analyze_fn(system: str):
    if system == "baseline":
        from baseline.baseline import analyze_project

        return analyze_project
    if system == "advanced":
        from assumption_hunter.workflow import analyze_project

        return analyze_project
    raise ValueError(f"Unknown system: {system}")


def run(system: str) -> dict:
    analyze_project = get_analyze_fn(system)
    case_results = []
    total_detected = 0
    total_ground_truth = 0

    for case in load_cases():
        project_path = str(REPO_ROOT / case["project_path"])
        start = time.time()
        try:
            report = analyze_project(project_path)
            error = None
        except Exception as exc:  # noqa: BLE001
            report = {"assumptions": []}
            error = str(exc)
        elapsed = time.time() - start

        detected, total, detected_ids = compute_recall(case["ground_truth"], report.get("assumptions", []))
        total_detected += detected
        total_ground_truth += total

        case_results.append(
            {
                "id": case["id"],
                "name": case["name"],
                "detected": detected,
                "total": total,
                "detected_ids": detected_ids,
                "recall": detected / total if total else 0.0,
                "elapsed_seconds": round(elapsed, 2),
                "raw_assumptions": report.get("assumptions", []),
                "error": error,
            }
        )
        status = f"{detected}/{total}" if error is None else f"ERROR: {error}"
        print(f"  {case['id']} ({case['name']}): {status}")

    overall_recall = total_detected / total_ground_truth if total_ground_truth else 0.0
    result = {
        "system": system,
        "overall_detected": total_detected,
        "overall_total": total_ground_truth,
        "overall_recall": overall_recall,
        "cases": case_results,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / f"{system}_results.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{system} overall recall: {total_detected}/{total_ground_truth} = {overall_recall:.1%}")
    print(f"Saved to {out_path}")
    return result


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("baseline", "advanced"):
        print("Usage: python evaluation/evaluate.py <baseline|advanced>")
        sys.exit(1)
    run(sys.argv[1])
