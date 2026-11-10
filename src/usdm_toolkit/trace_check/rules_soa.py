"""Schedule of Activities (USDM) vs collected SDTM findings data.

Planned = biomedical concepts scheduled at encounters in the USDM timelines.
Collected = rows in the mapped SDTM domain with ``--TESTCD`` at a VISIT.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass

from .matching import MatchResult, match_labels, normalize
from .model import Context, Finding, Rule, RuleSpec, distinct

CAT = "Schedule of Activities"


@dataclass(frozen=True)
class _Planned:
    domain: str
    testcd: str
    bc_names: tuple[str, ...]
    encounter_ids: tuple[str, ...]


def _planned(ctx: Context) -> tuple[tuple[_Planned, ...], tuple[str, ...]]:
    by_test: dict[tuple[str, str], dict] = {}
    unmapped: dict[str, None] = {}
    for p in ctx.view.soa:
        target = ctx.bc_map.get(p.bc_code)
        if target is None:
            unmapped.setdefault(f"{p.bc_name} ({p.bc_code or 'no code'})", None)
            continue
        slot = by_test.setdefault(target, {"names": {}, "encs": {}})
        slot["names"].setdefault(p.bc_name, None)
        slot["encs"].setdefault(p.encounter_id, None)
    planned = tuple(_Planned(d, t, tuple(s["names"]), tuple(s["encs"]))
                    for (d, t), s in by_test.items())
    return planned, tuple(unmapped)


def _collected(rows, domain: str, testcd: str) -> tuple[dict, ...]:
    var = f"{domain}TESTCD"
    return tuple(r for r in rows if str(r.get(var) or "").strip().upper() == testcd)


def _visit_match(ctx: Context, rows) -> MatchResult:
    return match_labels([e.label_item() for e in ctx.view.encounters],
                        distinct(rows, "VISIT"))


def _encounter_label(ctx: Context, encounter_id: str) -> str:
    enc = ctx.view.encounter(encounter_id)
    return enc.display if enc else encounter_id


def soa_unmapped(ctx: Context) -> Iterator[Finding]:
    _, unmapped = _planned(ctx)
    if unmapped:
        yield Finding("TC-SOA-000", "info", CAT,
                      f"{len(unmapped)} scheduled biomedical concept(s) have no "
                      "SDTM mapping and were not checked: "
                      + "; ".join(unmapped[:15]) + (" ..." if len(unmapped) > 15 else ""),
                      usdm_ref="biomedicalConcepts", sdtm_ref="(bc map)",
                      count=len(unmapped))


def soa_tests_collected(ctx: Context) -> Iterator[Finding]:
    planned, _ = _planned(ctx)
    missing_domains: dict[str, int] = defaultdict(int)
    for p in planned:
        rows = ctx.rows(p.domain)
        if not rows:
            missing_domains[p.domain] += 1
            continue
        if not _collected(rows, p.domain, p.testcd):
            yield Finding("TC-SOA-001", "warning", CAT,
                          f"{p.testcd} is scheduled in the SoA "
                          f"({', '.join(p.bc_names)}) but {p.domain} has no records",
                          usdm_ref=f"BC {', '.join(p.bc_names)}",
                          sdtm_ref=f"{p.domain}.{p.domain}TESTCD='{p.testcd}'")
    for domain, n in missing_domains.items():
        yield Finding("TC-SOA-001", "info", CAT,
                      f"{domain} dataset not provided; {n} scheduled test(s) not checked",
                      usdm_ref="scheduleTimelines", sdtm_ref=domain, count=n)


def soa_visits(ctx: Context) -> Iterator[Finding]:
    planned, _ = _planned(ctx)
    for p in planned:
        collected = _collected(ctx.rows(p.domain), p.domain, p.testcd)
        if not collected:
            continue  # TC-SOA-001 already covers this
        visits = _visit_match(ctx, ctx.rows(p.domain))
        have = {normalize(r.get("VISIT")) for r in collected}
        labels = [_encounter_label(ctx, e) for e in p.encounter_ids]
        planned_visits = {lab: visits.right_for(lab) for lab in labels}
        unnamed = [lab for lab, visit in planned_visits.items() if visit is None]
        missing = [lab for lab, visit in planned_visits.items()
                   if visit is not None and normalize(visit) not in have]
        expected = {normalize(v) for v in planned_visits.values() if v}
        extra = [pair.right for pair in visits.pairs
                 if normalize(pair.right) in have
                 and normalize(pair.right) not in expected]
        if missing:
            yield Finding("TC-SOA-002", "warning", CAT,
                          f"{p.testcd} planned at {', '.join(missing)} but no "
                          f"{p.domain} records at that visit",
                          usdm_ref=f"BC {', '.join(p.bc_names)}",
                          sdtm_ref=f"{p.domain}TESTCD='{p.testcd}'", count=len(missing))
        if unnamed:
            yield Finding("TC-SOA-002", "warning", CAT,
                          f"{p.testcd} planned at {', '.join(unnamed)} but no "
                          f"{p.domain}.VISIT label matches that encounter "
                          "(naming mismatch or visit never held)",
                          usdm_ref=f"BC {', '.join(p.bc_names)}",
                          sdtm_ref=f"{p.domain}.VISIT", count=len(unnamed))
        if extra:
            yield Finding("TC-SOA-003", "info", CAT,
                          f"{p.testcd} collected at {', '.join(extra)} where the SoA "
                          "does not schedule it",
                          usdm_ref=f"BC {', '.join(p.bc_names)}",
                          sdtm_ref=f"{p.domain}TESTCD='{p.testcd}'", count=len(extra))


RULES: tuple[Rule, ...] = (
    Rule((RuleSpec("TC-SOA-000", "Scheduled BCs have an SDTM mapping", CAT, "info"),),
         soa_unmapped),
    Rule((RuleSpec("TC-SOA-001", "Each scheduled test has SDTM records", CAT,
                   "warning"),), soa_tests_collected),
    Rule((RuleSpec("TC-SOA-002", "Scheduled test collected at each planned visit",
                   CAT, "warning"),
          RuleSpec("TC-SOA-003", "Test collected at visits not in the SoA", CAT,
                   "info")), soa_visits),
)
