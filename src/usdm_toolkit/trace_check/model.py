"""Core data types for trace-check: findings, rule specs and the report."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:  # pragma: no cover
    from .usdm_view import StudyView

Severity = Literal["error", "warning", "info"]
SEVERITIES: tuple[Severity, ...] = ("error", "warning", "info")

Rows = tuple[dict, ...]
SdtmData = Mapping[str, Rows]
BcMap = Mapping[str, tuple[str, str]]


@dataclass(frozen=True)
class Finding:
    """One cross-artifact inconsistency (or informational note)."""

    rule_id: str
    severity: Severity
    category: str
    message: str
    usdm_ref: str = ""
    sdtm_ref: str = ""
    count: int = 1


@dataclass(frozen=True)
class RuleSpec:
    """Static description of a rule, shown in the report's Rules sheet."""

    rule_id: str
    title: str
    category: str
    severity: Severity
    requires: tuple[str, ...] = ()


@dataclass(frozen=True)
class Skipped:
    rule_id: str
    reason: str


@dataclass(frozen=True)
class Context:
    """Everything a rule may look at. Rules must not mutate it."""

    view: StudyView
    sdtm: SdtmData
    bc_map: BcMap

    def rows(self, domain: str) -> Rows:
        return self.sdtm.get(domain.upper(), ())


RuleFn = Callable[[Context], Iterable[Finding]]


@dataclass(frozen=True)
class Rule:
    """A check function and every rule ID it can emit.

    ``specs[0].requires`` decides whether the check runs at all.
    """

    specs: tuple[RuleSpec, ...]
    check: RuleFn

    @property
    def requires(self) -> tuple[str, ...]:
        return self.specs[0].requires


@dataclass(frozen=True)
class TraceReport:
    findings: tuple[Finding, ...]
    rules: tuple[RuleSpec, ...]
    skipped: tuple[Skipped, ...] = field(default_factory=tuple)

    def summary(self) -> dict[str, int]:
        counts = {sev: 0 for sev in SEVERITIES}
        for f in self.findings:
            counts[f.severity] += 1
        counts["rules_run"] = len(self.rules) - len(self.skipped)
        counts["rules_skipped"] = len(self.skipped)
        return counts

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")


def distinct(rows: Rows, var: str) -> tuple[str, ...]:
    """Distinct non-blank values of ``var`` in first-seen order."""
    seen: dict[str, None] = {}
    for r in rows:
        val = r.get(var)
        if val is None:
            continue
        text = str(val).strip()
        if text:
            seen.setdefault(text, None)
    return tuple(seen)


def subject_count(rows: Rows, var: str, value: str) -> int:
    return len({r.get("USUBJID") for r in rows
                if str(r.get(var) or "").strip() == value})
