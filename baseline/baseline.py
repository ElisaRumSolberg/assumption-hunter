"""Baseline assumption detector: single prompt, no tools, no retry, no code execution."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from assumption_hunter.llm_client import extract_json, generate_text
from assumption_hunter.tools.file_reader import load_project

BASELINE_PROMPT = """Analyze this software project and identify hidden assumptions that
could cause failures or bugs.
For each assumption return: assumption, category, evidence, risk, and severity
(high/medium/low, where low means a true-but-marginal environment/toolchain nicety
rather than a real functional or security risk).
Return JSON only, in this exact schema:
{{
  "assumptions": [
    {{"assumption": "string", "category": "string", "evidence": "string (file path)", "risk": "string", "severity": "high|medium|low"}}
  ]
}}

Project:
{project}
"""


def analyze_project(project_path: str) -> dict:
    project_text = load_project(project_path)
    prompt = BASELINE_PROMPT.format(project=project_text)
    raw = generate_text(prompt)
    return extract_json(raw)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python baseline/baseline.py <project_path>")
        sys.exit(1)
    result = analyze_project(sys.argv[1])
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
