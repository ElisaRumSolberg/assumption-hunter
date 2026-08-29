"""Stage 1 (V1): Context + Assumption Analyzer.

Reads the project, infers its stack/domain, and mines candidate hidden
assumptions grouped by category. This is a wider net than the baseline: it
explicitly walks the fixed category list and asks for one evidence file per
candidate so the Evidence Checker has something concrete to verify.
"""

from assumption_hunter.llm_client import extract_json, generate_text
from assumption_hunter.tools.file_reader import load_project

CATEGORIES = ["data", "environment", "api", "time", "business_rule", "auth"]

CONTEXT_AND_ASSUMPTION_PROMPT = """You are the first stage of a two-stage assumption-detection
pipeline for software projects. Your job is to read the project below, understand its
stack and structure, then mine hidden assumptions the code makes without verifying them.

For each of these categories, look for at least one candidate assumption if one plausibly
exists in this project: {categories}.

A hidden assumption is something the code relies on being true but never checks
(e.g. a value is never null, a list is never empty, an env var is always set, an API
always responds a certain way, a timestamp is always in a certain timezone).

For each candidate assumption return:
- assumption: one sentence, the thing being assumed
- category: one of {categories}
- evidence: the exact relative file path where this assumption is made
- risk: what could go wrong if the assumption is false

Return JSON only, in this exact schema:
{{
  "assumptions": [
    {{"assumption": "string", "category": "string", "evidence": "string (file path)", "risk": "string"}}
  ]
}}

Project:
{project}
"""


def analyze(project_path: str) -> list[dict]:
    project_text = load_project(project_path)
    prompt = CONTEXT_AND_ASSUMPTION_PROMPT.format(categories=", ".join(CATEGORIES), project=project_text)
    raw = generate_text(prompt)
    return extract_json(raw).get("assumptions", [])
