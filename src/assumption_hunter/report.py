"""Renders an AssumptionReport dict as a readable report — the finished,
sign-off-able output a developer actually reads, instead of raw JSON.

Two renderers: `render_markdown` (plain .md text, for files/GitHub) and
`render_pretty` (an actual aligned table drawn in the terminal via `rich` —
raw markdown pipes/dashes are source syntax, not a rendered table, so they
look misaligned when printed straight to a terminal).
"""

_SEVERITY_STYLE = {"high": "bold red", "medium": "yellow", "low": "dim"}


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


def render_pretty(project_name: str, report: dict) -> None:
    """Prints an aligned, colored table straight to the terminal via `rich`."""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    assumptions = report.get("assumptions", [])

    console.print(f"\n[bold]Assumption Hunter Report[/bold] — {project_name}")
    console.print(f"Found [bold]{len(assumptions)}[/bold] hidden assumption(s) that could cause failures or bugs.\n")

    if not assumptions:
        console.print("No unverified assumptions were found in this project.")
        return

    table = Table(show_lines=True, expand=True)
    table.add_column("#", justify="right", style="dim", width=2, no_wrap=True)
    table.add_column("Sev", width=6, no_wrap=True)
    table.add_column("Category", width=14, no_wrap=True)
    table.add_column("Evidence", width=18, no_wrap=True, overflow="fold")
    table.add_column("Assumption", ratio=2)
    table.add_column("Risk", ratio=2)

    for i, a in enumerate(assumptions, start=1):
        severity = a.get("severity", "medium")
        style = _SEVERITY_STYLE.get(severity, "")
        table.add_row(
            str(i),
            f"[{style}]{severity.upper()}[/{style}]" if style else severity.upper(),
            a.get("category", ""),
            a.get("evidence", ""),
            a.get("assumption", ""),
            a.get("risk", ""),
        )

    console.print(table)
