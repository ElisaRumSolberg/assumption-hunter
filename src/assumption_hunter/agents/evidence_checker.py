"""Stage 2 (V1): Evidence Checker.

For each candidate assumption, reads the *actual* evidence file from disk
(not the LLM's memory of it) and asks the model whether the file content
really supports the claim. This is the piece the baseline has no equivalent
of: it can reject a candidate whose evidence file doesn't exist or doesn't
back up the claim, instead of reporting everything the miner produced.
"""

from assumption_hunter.llm_client import extract_json, generate_text
from assumption_hunter.tools.file_reader import read_file

EVIDENCE_CHECK_PROMPT = """You are the evidence-verification stage of an assumption-detection
pipeline. You are given one candidate assumption and the full content of the file cited as
its evidence. Decide whether the file content actually supports the claim.

Classify as exactly one of: SUPPORTED, PARTIALLY_SUPPORTED, UNVERIFIED, CONTRADICTED.
- SUPPORTED: the file clearly relies on this assumption with no guard/check for the opposite case.
- PARTIALLY_SUPPORTED: related behavior exists but the assumption as stated is broader than what the file shows.
- UNVERIFIED: the file doesn't contain enough to confirm or deny this specific claim.
- CONTRADICTED: the file already guards against this case (e.g. a null check, try/except, or default value).

Candidate assumption: {assumption}
Category: {category}
Claimed evidence file: {evidence_path}

File content:
{file_content}

Return JSON only, in this exact schema:
{{"status": "SUPPORTED|PARTIALLY_SUPPORTED|UNVERIFIED|CONTRADICTED", "note": "one sentence explaining the verdict"}}
"""


def check(project_path: str, candidate: dict) -> dict:
    evidence_path = (candidate.get("evidence") or "").strip()
    try:
        file_content = read_file(project_path, evidence_path)
    except OSError:
        return {**candidate, "status": "UNVERIFIED", "verification_note": f"Evidence file '{evidence_path}' not found in project."}

    prompt = EVIDENCE_CHECK_PROMPT.format(
        assumption=candidate.get("assumption", ""),
        category=candidate.get("category", ""),
        evidence_path=evidence_path,
        file_content=file_content,
    )
    raw = generate_text(prompt)
    result = extract_json(raw)
    return {
        **candidate,
        "status": result.get("status", "UNVERIFIED"),
        "verification_note": result.get("note", ""),
    }


def check_all(project_path: str, candidates: list[dict]) -> list[dict]:
    return [check(project_path, c) for c in candidates]
