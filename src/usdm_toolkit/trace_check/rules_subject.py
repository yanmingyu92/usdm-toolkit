"""Protocol (USDM) vs subject-level SDTM data: DM, SV, SE, EX."""

from __future__ import annotations

from collections.abc import Iterator

from .matching import match_labels, normalize
from .model import Context, Finding, Rule, RuleSpec, distinct, subject_count
from .rules_design import approx_notes

CAT = "Subject Data"

# SDTMIG null-arm conventions: never expected to be a protocol arm.
NON_ARM_CODES = frozenset({"SCRNFAIL", "NOTASSGN", "NOTTRT", "UNPLAN"})
NON_ARM_LABELS = frozenset({"screen failure", "not assigned", "not treated",
                            "unplanned treatment"})
UNSCHEDULED_PREFIXES = ("unsched", "unscheduled")


def _is_arm(code: object, label: object) -> bool:
    c = str(code or "").strip().upper()
    return bool(str(label or "").strip()) and c not in NON_ARM_CODES \
        and normalize(label) not in NON_ARM_LABELS


def _code(value: object) -> str:
    return str(value or "").strip()


def _unscheduled(label: object) -> bool:
    return normalize(label).startswith(UNSCHEDULED_PREFIXES)


def dm_arms(ctx: Context) -> Iterator[Finding]:
    dm = ctx.rows("DM")
    arms = [a.label_item() for a in ctx.view.arms]
    for code_var, label_var in (("ARMCD", "ARM"), ("ACTARMCD", "ACTARM")):
        values = tuple(dict.fromkeys(
            str(r.get(label_var)).strip() for r in dm
            if _is_arm(r.get(code_var), r.get(label_var))))
        result = match_labels(arms, values)
        for value in result.right_only:
            yield Finding("TC-DM-001", "error", CAT,
                          f"DM.{label_var} '{value}' is not a protocol arm",
                          usdm_ref="StudyDesign.arms",
                          sdtm_ref=f"DM.{label_var}='{value}'",
                          count=subject_count(dm, label_var, value))
        yield from approx_notes("TC-DM-001", CAT, result, f"DM.{label_var}")


def dm_actual_vs_planned(ctx: Context) -> Iterator[Finding]:
    dm = ctx.rows("DM")
    if dm and "ACTARMCD" not in dm[0]:
        return
    diff = [r for r in dm
            if _code(r.get("ARMCD")) and _code(r.get("ACTARMCD"))
            and _is_arm(r.get("ARMCD"), r.get("ARM"))
            and _is_arm(r.get("ACTARMCD"), r.get("ACTARM"))
            and _code(r.get("ARMCD")) != _code(r.get("ACTARMCD"))]
    if diff:
        pairs = sorted({f"{r.get('ARMCD')}->{r.get('ACTARMCD')}" for r in diff})
        yield Finding("TC-DM-002", "info", CAT,
                      f"{len(diff)} subject(s) received a different arm than "
                      f"planned ({', '.join(pairs)}); confirm against protocol "
                      "deviations and the reviewer's guide",
                      usdm_ref="StudyDesign.arms", sdtm_ref="DM.ARMCD vs DM.ACTARMCD",
                      count=len(diff))


def sv_visits(ctx: Context) -> Iterator[Finding]:
    sv = ctx.rows("SV")
    visits = tuple(v for v in distinct(sv, "VISIT") if not _unscheduled(v))
    scheduled = [e.label_item() for e in ctx.view.encounters
                 if not _unscheduled(e.display)]
    result = match_labels(scheduled, visits)
    for visit in result.right_only:
        yield Finding("TC-SV-001", "warning", CAT,
                      f"SV visit '{visit}' is not a protocol encounter",
                      usdm_ref="StudyDesign.encounters",
                      sdtm_ref=f"SV.VISIT='{visit}'",
                      count=subject_count(sv, "VISIT", visit))
    for enc in result.left_only:
        yield Finding("TC-SV-002", "warning", CAT,
                      f"Protocol encounter '{enc}' has no SV records",
                      usdm_ref=f"Encounter '{enc}'", sdtm_ref="SV.VISIT", count=0)
    yield from approx_notes("TC-SV-001", CAT, result, "Visit")


def se_elements(ctx: Context) -> Iterator[Finding]:
    se = ctx.rows("SE")
    result = match_labels([e.label_item() for e in ctx.view.elements],
                          distinct(se, "ELEMENT"))
    for el in result.right_only:
        yield Finding("TC-SE-001", "warning", CAT,
                      f"SE element '{el}' is not a protocol element",
                      usdm_ref="StudyDesign.elements", sdtm_ref=f"SE.ELEMENT='{el}'",
                      count=subject_count(se, "ELEMENT", el))
    yield from approx_notes("TC-SE-001", CAT, result, "Element")


def ex_treatments(ctx: Context) -> Iterator[Finding]:
    ex = ctx.rows("EX")
    result = match_labels([t.label_item() for t in ctx.view.treatments],
                          distinct(ex, "EXTRT"))
    for trt in result.right_only:
        yield Finding("TC-EX-001", "warning", CAT,
                      f"EX.EXTRT '{trt}' matches no protocol intervention or product",
                      usdm_ref="studyInterventions / administrableProducts",
                      sdtm_ref=f"EX.EXTRT='{trt}'",
                      count=subject_count(ex, "EXTRT", trt))
    # Treatment names must be spelled identically: approximate = warning.
    yield from approx_notes("TC-EX-001", CAT, result,
                            "Treatment name (possible spelling inconsistency)",
                            severity="warning")


def _spec(rule_id: str, title: str, severity: str, requires: str) -> RuleSpec:
    return RuleSpec(rule_id, title, CAT, severity, (requires,))


RULES: tuple[Rule, ...] = (
    Rule((_spec("TC-DM-001", "DM planned/actual arms are protocol arms", "error",
                "DM"),), dm_arms),
    Rule((_spec("TC-DM-002", "Subjects whose actual arm differs from planned",
                "info", "DM"),), dm_actual_vs_planned),
    Rule((_spec("TC-SV-001", "SV scheduled visits are protocol encounters",
                "warning", "SV"),
          _spec("TC-SV-002", "Protocol encounters have SV records", "warning",
                "SV")), sv_visits),
    Rule((_spec("TC-SE-001", "SE elements are protocol elements", "warning",
                "SE"),), se_elements),
    Rule((_spec("TC-EX-001", "EX treatments match protocol interventions",
                "warning", "EX"),), ex_treatments),
)
