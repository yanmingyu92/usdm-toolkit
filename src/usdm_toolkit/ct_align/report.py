"""Markdown / JSON report generation for ct-align findings."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict
from datetime import date

from .checker import Finding

RULE_TITLES = {
    "CLASS_NOT_IN_CT": "Classes in dataStructure.yml without a CT entity row",
    "CLASS_CCODE_MISMATCH": "Class-level C-code mismatches",
    "CLASS_TERM_MISMATCH": "Class-level preferred term mismatches",
    "CLASS_DEFINITION_MISMATCH": "Class-level definition mismatches",
    "ATTR_NOT_IN_CT": "YAML attributes with a C-code but no CT row",
    "ATTR_CCODE_MISMATCH": "Attribute-level C-code mismatches",
    "ATTR_TERM_MISMATCH": "Attribute-level preferred term mismatches",
    "ATTR_DEFINITION_MISMATCH": "Attribute-level definition mismatches",
    "CCODE_NOT_IN_CT": "YAML C-codes not found in USDM_CT.xlsx",
    "CT_ATTR_NOT_IN_YAML": "CT rows without a YAML C-code counterpart (coverage)",
    "CLASSIFICATION_WITHOUT_VALUE_LIST": "Classification-style definitions without a value list",
    "VALUE_LIST_TYPE_MISMATCH": "Value list vs. YAML type inconsistencies",
}

RULE_ORDER = list(RULE_TITLES)


def _esc(value: str | None) -> str:
    if value is None:
        return "-"
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(
    findings: list[Finding],
    *,
    yaml_source: str,
    ct_source: str,
    report_date: date | None = None,
) -> str:
    report_date = report_date or date.today()
    counts = Counter(f.rule for f in findings)
    lines: list[str] = []
    lines.append("# ct-align consistency report")
    lines.append("")
    lines.append(f"- Report date: {report_date.isoformat()}")
    lines.append(f"- Model file: `{yaml_source}`")
    lines.append(f"- CT file: `{ct_source}`")
    lines.append(f"- Total findings: {len(findings)}")
    lines.append("")
    lines.append("## Summary by rule")
    lines.append("")
    lines.append("| Rule | Severity | Count |")
    lines.append("| --- | --- | --- |")
    severity = {}
    for f in findings:
        severity.setdefault(f.rule, f.severity)
    for rule in RULE_ORDER:
        if counts.get(rule):
            lines.append(f"| `{rule}` | {severity[rule]} | {counts[rule]} |")
    lines.append("")
    for rule in RULE_ORDER:
        group = [f for f in findings if f.rule == rule]
        if not group:
            continue
        lines.append(f"## {RULE_TITLES[rule]} (`{rule}`, {len(group)})")
        lines.append("")
        lines.append("| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for f in group:
            lines.append(
                f"| {_esc(f.location)} | {_esc(f.ccode_yaml)} | {_esc(f.ccode_ct)} "
                f"| {_esc(f.yaml_value)} | {_esc(f.ct_value)} | {_esc(f.message)} |"
            )
        lines.append("")
    return "\n".join(lines)


def render_json(findings: list[Finding]) -> str:
    return json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False)
