"""CLI entry point: python -m assumption_hunter.cli <project_path> [--baseline]"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assumption_hunter.report import render_markdown, render_pretty
from assumption_hunter.workflow import analyze_project as analyze_advanced


def main() -> None:
    parser = argparse.ArgumentParser(description="Assumption Hunter: find hidden assumptions in a software project.")
    parser.add_argument("project_path", help="Path to the project to analyze")
    parser.add_argument("--baseline", action="store_true", help="Use the single-prompt baseline instead of the advanced pipeline")
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "pretty"],
        default="json",
        help="Output format: json, markdown (plain .md text), or pretty (aligned table in the terminal, default: json)",
    )
    args = parser.parse_args()

    if args.baseline:
        repo_root = Path(__file__).resolve().parent.parent.parent
        sys.path.insert(0, str(repo_root))
        from baseline.baseline import analyze_project as analyze_baseline

        report = analyze_baseline(args.project_path)
    else:
        report = analyze_advanced(args.project_path)

    project_name = Path(args.project_path).resolve().name
    if args.format == "markdown":
        print(render_markdown(project_name, report))
    elif args.format == "pretty":
        render_pretty(project_name, report)
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
