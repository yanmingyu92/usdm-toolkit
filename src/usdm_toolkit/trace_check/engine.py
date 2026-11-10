"""Run every trace-check rule against one USDM study and its SDTM datasets."""

from __future__ import annotations

from collections.abc import Mapping

from . import rules_design, rules_soa, rules_subject, rules_summary
from .bc_map import merged
from .model import (BcMap, Context, Finding, Rule, Rows, Skipped, TraceReport)
from .usdm_view import StudyView

ALL_RULES: tuple[Rule, ...] = (
    rules_design.RULES + rules_summary.RULES + rules_subject.RULES + rules_soa.RULES
)
_SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def run_trace_check(usdm: dict, sdtm: Mapping[str, Rows], *,
                    bc_map: BcMap | None = None,
                    rules: tuple[Rule, ...] = ALL_RULES) -> TraceReport:
    """Check a USDM study against SDTM datasets keyed by domain name."""
    data = {str(k).upper(): tuple(v) for k, v in sdtm.items()}
    ctx = Context(view=StudyView.from_usdm(usdm), sdtm=data, bc_map=merged(bc_map))

    findings: list[Finding] = []
    skipped: list[Skipped] = []
    for rule in rules:
        missing = [d for d in rule.requires if not data.get(d)]
        if missing:
            skipped.extend(Skipped(s.rule_id, f"dataset(s) not provided: "
                                   f"{', '.join(missing)}") for s in rule.specs)
            continue
        try:
            findings.extend(list(rule.check(ctx)))
        except Exception as exc:  # noqa: BLE001 - one bad rule must not stop the run
            reason = f"rule raised {type(exc).__name__}: {exc}"
            skipped.extend(Skipped(s.rule_id, reason) for s in rule.specs)

    ordered = sorted(findings, key=lambda f: (_SEVERITY_ORDER[f.severity],
                                              f.rule_id))
    return TraceReport(findings=tuple(ordered),
                       rules=tuple(s for r in rules for s in r.specs),
                       skipped=tuple(skipped))
