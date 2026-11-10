"""Render a TraceReport as Markdown, JSON, or a P21-style Excel workbook."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .. import __version__
from .model import TraceReport

ISSUE_COLUMNS = ("Rule ID", "Severity", "Category", "Message", "USDM Reference",
                 "SDTM Reference", "Count")
_FILL = {"error": "F8CBAD", "warning": "FFE699", "info": "DDEBF7"}
_MAX_COL_WIDTH = 80
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cell(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_markdown(report: TraceReport, *, usdm_source: str = "",
                    sdtm_source: str = "") -> str:
    s = report.summary()
    lines = [
        "# trace-check report", "",
        f"- Generated: {_now()} (usdm-toolkit {__version__})",
        f"- USDM: `{usdm_source}`", f"- SDTM: `{sdtm_source}`",
        f"- Findings: **{s['error']} error(s), {s['warning']} warning(s), "
        f"{s['info']} info**",
        f"- Rules run: {s['rules_run']}, skipped: {s['rules_skipped']}", "",
        "| Rule | Severity | Category | Message | USDM | SDTM | Count |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += [f"| {f.rule_id} | {f.severity} | {f.category} | {_cell(f.message)} | "
              f"{_cell(f.usdm_ref)} | {_cell(f.sdtm_ref)} | {f.count} |"
              for f in report.findings]
    if report.skipped:
        lines += ["", "## Skipped rules", ""]
        lines += [f"- {sk.rule_id}: {sk.reason}" for sk in report.skipped]
    return "\n".join(lines) + "\n"


def render_json(report: TraceReport) -> str:
    return json.dumps({
        "generated": _now(),
        "tool": f"usdm-toolkit {__version__}",
        "summary": report.summary(),
        "findings": [asdict(f) for f in report.findings],
        "rules": [asdict(r) for r in report.rules],
        "skipped": [asdict(sk) for sk in report.skipped],
    }, indent=2)


def write_xlsx(report: TraceReport, path: str | Path, *, usdm_source: str = "",
               sdtm_source: str = "") -> Path:
    wb = Workbook()
    _summary_sheet(wb.active, report, usdm_source, sdtm_source)
    _issues_sheet(wb.create_sheet("Issues"), report)
    _rules_sheet(wb.create_sheet("Rules"), report)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out


def _header(ws, columns) -> None:
    ws.append(list(columns))
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "A2"


def _autosize(ws) -> None:
    for idx, col in enumerate(ws.columns, start=1):
        width = max((len(str(c.value or "")) for c in col), default=8)
        ws.column_dimensions[get_column_letter(idx)].width = min(width + 2,
                                                                 _MAX_COL_WIDTH)


def _summary_sheet(ws, report, usdm_source, sdtm_source) -> None:
    ws.title = "Summary"
    s = report.summary()
    for row in (("trace-check report", ""), ("Generated (UTC)", _now()),
                ("Tool", f"usdm-toolkit {__version__}"),
                ("USDM", usdm_source), ("SDTM", sdtm_source),
                ("Errors", s["error"]), ("Warnings", s["warning"]),
                ("Info", s["info"]), ("Rules run", s["rules_run"]),
                ("Rules skipped", s["rules_skipped"])):
        ws.append(row)
    ws["A1"].font = Font(bold=True, size=14)
    _autosize(ws)


def _safe(value: object) -> object:
    """Stop text read from study files being run as a spreadsheet formula."""
    if isinstance(value, str) and value[:1] in _FORMULA_PREFIXES:
        return "'" + value
    return value


def _issues_sheet(ws, report) -> None:
    _header(ws, ISSUE_COLUMNS)
    for f in report.findings:
        ws.append([_safe(v) for v in (f.rule_id, f.severity, f.category, f.message,
                                      f.usdm_ref, f.sdtm_ref)] + [f.count])
        ws.cell(ws.max_row, 2).fill = PatternFill("solid", fgColor=_FILL[f.severity])
    ws.auto_filter.ref = ws.dimensions
    _autosize(ws)


def _rules_sheet(ws, report) -> None:
    _header(ws, ("Rule ID", "Title", "Category", "Default Severity",
                 "Requires", "Status", "Findings"))
    skipped = {sk.rule_id: sk.reason for sk in report.skipped}
    for r in report.rules:
        n = sum(1 for f in report.findings if f.rule_id == r.rule_id)
        ws.append([r.rule_id, r.title, r.category, r.severity,
                   ", ".join(r.requires), skipped.get(r.rule_id, "run"), n])
    _autosize(ws)
