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


def _singularize(word: str) -> str:
    if len(word) > 4 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """Tokenize, singularize (crude, suffix-stripping) and also split
    snake_case identifiers into parts, so `event_time` contributes both
    `event_time` and `event`/`time`, and `datetimes` matches `datetime`.
    Ground-truth and model wording rarely match verbatim, so some tolerance
    for plurals and compound identifiers is needed for recall to mean
    anything on paraphrased output.
    """
    raw_words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    keywords = set()
    for word in raw_words:
        parts = [p for p in word.split("_") if p]
        for part in [word, *parts]:
            singular = _singularize(part)
            if singular not in _STOPWORDS and len(singular) > 2:
                keywords.add(singular)
    return keywords


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


def _trap_triggered(trap: dict, detected_assumption: dict) -> bool:
    """A trap is only "triggered" if the detected assumption is actually
    about the trap's distinguishing subject (e.g. email), not merely if it
    shares generic template words ("user", "non-null", "address") with the
    trap sentence. Plain keyword-overlap matching (as used for recall) is too
    permissive here: two unrelated "every X has a non-null Y" assumptions
    can share 4 of 5 keywords without ever mentioning the same field.

    `required_keywords` in ground_truth.json names the word(s) that must be
    present for a detected assumption to actually be about the trap.
    """
    required = trap.get("required_keywords")
    required_any_of = trap.get("required_any_of_keywords")
    if not required:
        trap_as_gt = {"assumption": trap["description"]}
        return matches(trap_as_gt, detected_assumption)

    detected_text = " ".join(
        [
            detected_assumption.get("assumption", ""),
            detected_assumption.get("evidence", ""),
            detected_assumption.get("risk", ""),
        ]
    )
    detected_keywords = _keywords(detected_text)
    if not all(kw.lower() in detected_keywords for kw in required):
        return False
    if required_any_of and not any(kw.lower() in detected_keywords for kw in required_any_of):
        return False
    return True


def compute_false_positives(trap_items: list[dict], detected_assumptions: list[dict]) -> tuple[int, int, list[str]]:
    """Traps are assumptions that LOOK plausible but are already guarded in
    the code. A system that reports one has pattern-matched on surface
    similarity instead of checking evidence — that's a false positive."""
    triggered_ids = []
    for trap in trap_items:
        if any(_trap_triggered(trap, d) for d in detected_assumptions):
            triggered_ids.append(trap["id"])
    return len(triggered_ids), len(trap_items), triggered_ids
