"""Renders an AssumptionReport dict as a readable Markdown report — the
finished, sign-off-able output a developer actually reads, instead of raw
JSON.
"""


def render_markdown(project_name: str, report: dict) -> str:
    assumptions = report.get("assumptions", [])
    lines = [
        f"# Assumption Hunter Report — {project_name}",
        "",
        f"Found **{len(assumptions)}** hidden assumption(s) that could cause failures or bugs.",
        "",
    ]

    if not assumptions:
        lines.append("No unverified assumptions were found in this project.")
        return "\n".join(lines)

    by_category: dict[str, list[dict]] = {}
    for a in assumptions:
        by_category.setdefault(a.get("category", "uncategorized"), []).append(a)

    lines.append("## Summary by category")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for category, items in sorted(by_category.items()):
        lines.append(f"| {category} | {len(items)} |")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    for i, a in enumerate(assumptions, start=1):
        severity = a.get("severity", "medium")
        lines.append(f"### {i}. [{severity.upper()}] {a.get('assumption', '(no assumption text)')}")
        lines.append("")
        lines.append(f"- **Category:** {a.get('category', 'unknown')}")
        lines.append(f"- **Severity:** {severity}")
        lines.append(f"- **Evidence:** `{a.get('evidence', 'unknown')}`")
        lines.append(f"- **Risk:** {a.get('risk', 'unknown')}")
        lines.append("")

    return "\n".join(lines)
