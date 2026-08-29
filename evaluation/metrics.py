"""Recall metric: how many ground-truth assumptions did the system detect.

Matching starts as keyword overlap between the ground-truth assumption
sentence and each detected assumption's `assumption` + `evidence` text, using
a small stopword list so short function/variable names still count.
"""

import re

_STOPWORDS = {
    "a", "an", "the", "is", "are", "always", "never", "every", "any", "all",
    "may", "might", "will", "would", "should", "could", "can", "must",
    "to", "of", "in", "on", "at", "for", "with", "and", "or", "but", "not",
    "be", "been", "being", "has", "have", "had", "it", "its", "that", "this",
    "when", "if", "as", "by", "from", "code", "assumes", "assume",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def matches(ground_truth_assumption: dict, detected_assumption: dict) -> bool:
    gt_text = ground_truth_assumption["assumption"]
    detected_text = " ".join(
        [
            detected_assumption.get("assumption", ""),
            detected_assumption.get("evidence", ""),
            detected_assumption.get("risk", ""),
        ]
    )
    gt_keywords = _keywords(gt_text)
    detected_keywords = _keywords(detected_text)
    if not gt_keywords:
        return False
    overlap = gt_keywords & detected_keywords
    return len(overlap) / len(gt_keywords) >= 0.4


def compute_recall(ground_truth_items: list[dict], detected_assumptions: list[dict]) -> tuple[int, int, list[str]]:
    detected_ids = []
    for gt in ground_truth_items:
        if any(matches(gt, d) for d in detected_assumptions):
            detected_ids.append(gt["id"])
    return len(detected_ids), len(ground_truth_items), detected_ids
