"""Protocol (USDM) vs submitted SDTM trial-design datasets: TA, TE, TV, TI."""

from __future__ import annotations

import re
from collections.abc import Iterator

from .matching import (MatchResult, containment, match_labels, normalize,
                       text_similarity)
from .model import Context, Finding, Rule, RuleSpec, distinct

CAT = "Trial Design"
TEXT_SIMILARITY_MIN = 0.8
ABBREVIATION_CONTAINMENT_MIN = 0.8


def approx_notes(rule_id: str, category: str, result: MatchResult, what: str,
                 severity: str = "info") -> Iterator[Finding]:
    """Report fuzzy (non-exact) pairings so a reviewer can confirm them."""
    for p in result.approximate:
        yield Finding(rule_id, severity, category,
                      f"{what} matched approximately (score {p.score:.2f}); "
                      "confirm the labels refer to the same thing",
                      usdm_ref=p.left, sdtm_ref=p.right)


# ---------------------------------------------------------------------------
# TA
# ---------------------------------------------------------------------------

def _rows_for_arm(ta, arm: str) -> tuple[dict, ...]:
    return tuple(r for r in ta if str(r.get("ARM") or "").strip() == arm)


def _order(row: dict) -> float:
    """TAETORD as a number; blanks and non-numbers sort last."""
    try:
        return float(str(row.get("TAETORD")).strip())
    except (TypeError, ValueError):
        return float("inf")


def _arm_match(ctx: Context) -> MatchResult:
    ta = ctx.rows("TA")
    sdtm_arms = [(arm, (arm, *distinct(_rows_for_arm(ta, arm), "ARMCD")))
                 for arm in distinct(ta, "ARM")]
    return match_labels([a.label_item() for a in ctx.view.arms], sdtm_arms)


def ta_arm_missing(ctx: Context) -> Iterator[Finding]:
    result = _arm_match(ctx)
    for arm in result.left_only:
        yield Finding("TC-TA-001", "error", CAT,
                      f"Protocol arm '{arm}' has no rows in TA",
                      usdm_ref=f"StudyArm '{arm}'", sdtm_ref="TA.ARM")
    yield from approx_notes("TC-TA-001", CAT, result, "Arm")


def ta_arm_extra(ctx: Context) -> Iterator[Finding]:
    for arm in _arm_match(ctx).right_only:
        yield Finding("TC-TA-002", "error", CAT,
                      f"TA arm '{arm}' is not a protocol arm",
                      usdm_ref="StudyDesign.arms", sdtm_ref=f"TA.ARM='{arm}'")


def ta_epochs(ctx: Context) -> Iterator[Finding]:
    result = match_labels([e.label_item() for e in ctx.view.epochs],
                          distinct(ctx.rows("TA"), "EPOCH"))
    for epoch in result.left_only:
        yield Finding("TC-TA-003", "warning", CAT,
                      f"Protocol epoch '{epoch}' is not used in TA.EPOCH",
                      usdm_ref=f"StudyEpoch '{epoch}'", sdtm_ref="TA.EPOCH")
    for epoch in result.right_only:
        yield Finding("TC-TA-003", "warning", CAT,
                      f"TA.EPOCH '{epoch}' is not a protocol epoch",
                      usdm_ref="StudyDesign.epochs", sdtm_ref=f"TA.EPOCH='{epoch}'")


def _element_match(ctx: Context) -> MatchResult:
    sdtm = distinct(ctx.rows("TE") + ctx.rows("TA"), "ELEMENT")
    return match_labels([e.label_item() for e in ctx.view.elements], sdtm)


def ta_element_sequence(ctx: Context) -> Iterator[Finding]:
    arms = _arm_match(ctx)
    elements = _element_match(ctx)
    ta = ctx.rows("TA")
    labels = {a.id: a.display for a in ctx.view.arms}
    for arm_id, usdm_path in ctx.view.arm_paths.items():
        sdtm_arm = arms.right_for(labels.get(arm_id, ""))
        if sdtm_arm is None:
            continue  # reported by TC-TA-001
        planned = [normalize(elements.right_for(el) or el) for el in usdm_path]
        rows = sorted(_rows_for_arm(ta, sdtm_arm), key=_order)
        actual = [normalize(r.get("ELEMENT")) for r in rows]
        if planned != actual:
            yield Finding("TC-TA-004", "warning", CAT,
                          f"Element sequence for arm '{sdtm_arm}' differs: "
                          f"protocol [{' > '.join(usdm_path)}] vs TA "
                          f"[{' > '.join(str(r.get('ELEMENT')) for r in rows)}]",
                          usdm_ref=f"StudyArm '{labels.get(arm_id)}' cells",
                          sdtm_ref=f"TA.ARM='{sdtm_arm}'")


# ---------------------------------------------------------------------------
# TE / TV
# ---------------------------------------------------------------------------

def te_elements(ctx: Context) -> Iterator[Finding]:
    result = match_labels([e.label_item() for e in ctx.view.elements],
                          distinct(ctx.rows("TE"), "ELEMENT"))
    for el in result.left_only:
        yield Finding("TC-TE-001", "warning", CAT,
                      f"Protocol element '{el}' is missing from TE",
                      usdm_ref=f"StudyElement '{el}'", sdtm_ref="TE.ELEMENT")
    for el in result.right_only:
        yield Finding("TC-TE-002", "warning", CAT,
                      f"TE element '{el}' is not a protocol element",
                      usdm_ref="StudyDesign.elements", sdtm_ref=f"TE.ELEMENT='{el}'")
    yield from approx_notes("TC-TE-001", CAT, result, "Element")


def tv_visits(ctx: Context) -> Iterator[Finding]:
    result = match_labels([e.label_item() for e in ctx.view.encounters],
                          distinct(ctx.rows("TV"), "VISIT"))
    for enc in result.left_only:
        yield Finding("TC-TV-001", "warning", CAT,
                      f"Protocol encounter '{enc}' has no planned visit in TV",
                      usdm_ref=f"Encounter '{enc}'", sdtm_ref="TV.VISIT")
    for visit in result.right_only:
        yield Finding("TC-TV-002", "warning", CAT,
                      f"TV visit '{visit}' is not a protocol encounter",
                      usdm_ref="StudyDesign.encounters", sdtm_ref=f"TV.VISIT='{visit}'")
    yield from approx_notes("TC-TV-001", CAT, result, "Visit")


# ---------------------------------------------------------------------------
# TI
# ---------------------------------------------------------------------------

def _ti_key(row: dict) -> tuple[str, int | None]:
    cat = "EXCLUSION" if "EXCL" in str(row.get("IECAT") or "").upper() else "INCLUSION"
    digits = re.findall(r"\d+", str(row.get("IETESTCD") or ""))
    return cat, int(digits[-1]) if digits else None


def _ref(key: tuple[str, int | None]) -> str:
    number = "(unnumbered)" if key[1] is None else key[1]
    return f"{key[0].title()} criterion {number}"


def _duplicates(keys: list[tuple[str, int | None]], where: str,
                usdm_ref: str, sdtm_ref: str) -> Iterator[Finding]:
    seen: set = set()
    for key in keys:
        if key in seen:
            yield Finding("TC-TI-001", "warning", CAT,
                          f"{_ref(key)} appears more than once in {where}; only "
                          "the first is compared",
                          usdm_ref=usdm_ref, sdtm_ref=sdtm_ref)
        seen.add(key)


def ti_criteria(ctx: Context) -> Iterator[Finding]:
    ti_rows = ctx.rows("TI")
    yield from _duplicates([_ti_key(r) for r in ti_rows], "TI", "", "TI")
    yield from _duplicates([(c.category, c.number) for c in ctx.view.criteria],
                           "the protocol", "eligibilityCriteria", "")
    ti: dict = {}
    for r in ti_rows:
        ti.setdefault(_ti_key(r), r)
    planned: dict = {}
    for c in ctx.view.criteria:
        planned.setdefault((c.category, c.number), c)
    abbreviated: list[str] = []
    for key, crit in planned.items():
        row = ti.get(key)
        ref = _ref(key)
        if row is None:
            yield Finding("TC-TI-001", "warning", CAT,
                          f"{ref} is not in TI", usdm_ref=f"EligibilityCriterion {crit.id}",
                          sdtm_ref="TI")
            continue
        ietest = row.get("IETEST")
        score = text_similarity(crit.text, ietest)
        if score >= TEXT_SIMILARITY_MIN:
            continue
        if containment(ietest, crit.text) >= ABBREVIATION_CONTAINMENT_MIN:
            abbreviated.append(str(row.get("IETESTCD")))
            continue
        yield Finding("TC-TI-002", "warning", CAT,
                      f"{ref}: TI text differs from protocol (similarity "
                      f"{score:.2f}). Protocol: '{crit.text[:120]}'",
                      usdm_ref=f"EligibilityCriterion {crit.id}",
                      sdtm_ref=f"TI.IETESTCD='{row.get('IETESTCD')}'")
    if abbreviated:
        yield Finding("TC-TI-002", "info", CAT,
                      f"{len(abbreviated)} TI criterion text(s) are abbreviations of "
                      "the protocol text (IETEST is limited to 200 characters); "
                      "confirm nothing material was dropped: " + ", ".join(abbreviated),
                      usdm_ref="eligibilityCriterionItems", sdtm_ref="TI.IETEST",
                      count=len(abbreviated))
    for key, row in ti.items():
        if key not in planned:
            yield Finding("TC-TI-001", "warning", CAT,
                          f"TI criterion '{row.get('IETESTCD')}' is not in the protocol",
                          usdm_ref="StudyDesign.eligibilityCriteria",
                          sdtm_ref=f"TI.IETESTCD='{row.get('IETESTCD')}'")


def _spec(rule_id: str, title: str, severity: str, requires: str) -> RuleSpec:
    return RuleSpec(rule_id, title, CAT, severity, (requires,))


RULES: tuple[Rule, ...] = (
    Rule((_spec("TC-TA-001", "Protocol arm present in TA", "error", "TA"),),
         ta_arm_missing),
    Rule((_spec("TC-TA-002", "TA arm defined in protocol", "error", "TA"),),
         ta_arm_extra),
    Rule((_spec("TC-TA-003", "TA epochs match protocol epochs", "warning", "TA"),),
         ta_epochs),
    Rule((_spec("TC-TA-004", "TA element sequence per arm matches protocol",
                "warning", "TA"),), ta_element_sequence),
    Rule((_spec("TC-TE-001", "Protocol element present in TE", "warning", "TE"),
          _spec("TC-TE-002", "TE element defined in protocol", "warning", "TE")),
         te_elements),
    Rule((_spec("TC-TV-001", "Protocol encounter present in TV", "warning", "TV"),
          _spec("TC-TV-002", "TV visit defined in protocol", "warning", "TV")),
         tv_visits),
    Rule((_spec("TC-TI-001", "Eligibility criteria correspond one-to-one with TI",
                "warning", "TI"),
          _spec("TC-TI-002", "TI criterion text matches protocol text", "warning",
                "TI")), ti_criteria),
)
