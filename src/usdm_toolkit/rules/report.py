"""Markdown / JSON report generation for rules-module violations."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import date

from .engine import Rule, Violation


def _esc(value: str | None) -> str:
    if value is None:
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(
    violations: list[Violation],
    rules: list[Rule],
    *,
    input_source: str,
    report_date: date | None = None,
) -> str:
    report_date = report_date or date.today()
    lines: list[str] = []
    lines.append("# USDM conformance rules report")
    lines.append("")
    lines.append(f"- Report date: {report_date.isoformat()}")
    lines.append(f"- Input: `{input_source}`")
    lines.append(f"- Rules evaluated: {len(rules)}")
    lines.append(f"- Total violations: {len(violations)}")
    lines.append("")
    lines.append("## Rules")
    lines.append("")
    lines.append("| Rule | Severity | Scope | Description |")
    lines.append("| --- | --- | --- | --- |")
    for rule in rules:
        lines.append(
            f"| `{rule.id}` | {rule.severity} | `{rule.scope}` "
            f"| {_esc(rule.description)} |"
        )
    lines.append("")
    if violations:
        counts = Counter(v.rule_id for v in violations)
        lines.append("## Violations")
        lines.append("")
        lines.append("| Rule | Severity | Node type | Node id | Detail |")
        lines.append("| --- | --- | --- | --- | --- |")
        for v in violations:
            lines.append(
                f"| `{v.rule_id}` | {v.severity} | {v.node_type} "
                f"| `{_esc(v.node_id)}` | {_esc(v.detail)} |"
            )
        lines.append("")
        lines.append("### Counts by rule")
        lines.append("")
        for rule_id, count in sorted(counts.items()):
            lines.append(f"- `{rule_id}`: {count}")
        lines.append("")
    else:
        lines.append("No violations found.")
        lines.append("")
    return "\n".join(lines)


def render_json(violations: list[Violation]) -> str:
    return json.dumps([asdict(v) for v in violations], indent=2, ensure_ascii=False)
