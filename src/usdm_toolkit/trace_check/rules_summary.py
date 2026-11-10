"""Protocol (USDM) vs SDTM Trial Summary (TS) parameters and objectives."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from .matching import (coded_compatible, containment, phase_compatible,
                       text_similarity)
from .model import Context, Finding, Rule, RuleSpec
from .usdm_view import StudyView

CAT = "Trial Summary"
TITLE_SIMILARITY_MIN = 0.9
OBJECTIVE_SIMILARITY_MIN = 0.8
TSVAL_MAX_LEN = 200          # SDTMIG: longer text continues in TSVAL1..TSVALn
TRUNCATED_CONTAINMENT_MIN = 0.9


def _same_number(usdm: str, ts: str) -> bool:
    try:
        return int(float(usdm)) == int(float(ts))
    except (TypeError, ValueError, OverflowError):
        return False


def _text_agrees(usdm: str, ts: str, minimum: float) -> bool:
    """Equal enough, or ``ts`` is a 200-character truncation of ``usdm``."""
    if text_similarity(usdm, ts) >= minimum:
        return True
    return len(ts) >= TSVAL_MAX_LEN - 10 and \
        containment(ts, usdm) >= TRUNCATED_CONTAINMENT_MIN


def _same_text(usdm: str, ts: str) -> bool:
    return _text_agrees(usdm, ts, TITLE_SIMILARITY_MIN)


def _same_id(usdm: str, ts: str) -> bool:
    return usdm.strip().upper() == ts.strip().upper()


# TSPARMCD -> (USDM source description, value getter, comparison)
_PARAMS: dict[str, tuple[str, Callable[[StudyView], str],
                         Callable[[str, str], bool]]] = {
    "TITLE": ("Official study title", lambda v: v.title, _same_text),
    "TPHASE": ("StudyDesign.studyPhase", lambda v: v.phase, phase_compatible),
    "TBLIND": ("StudyDesign.blindingSchema", lambda v: v.blinding, coded_compatible),
    "PLANSUB": ("population.plannedEnrollmentNumber",
                lambda v: "" if v.planned_enrollment is None
                else str(v.planned_enrollment), _same_number),
    "REGID": ("Registry study identifier", lambda v: v.registry_id, _same_id),
    "SPONSOR": ("Sponsor organization name", lambda v: v.sponsor_name, _same_text),
}


def _full_tsval(row: dict) -> str:
    """TSVAL plus any TSVAL1..TSVALn continuation columns."""
    parts = [str(row.get("TSVAL") or "")]
    n = 1
    while f"TSVAL{n}" in row:
        parts.append(str(row.get(f"TSVAL{n}") or ""))
        n += 1
    return "".join(parts).strip()


def _ts_values(ctx: Context) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in ctx.rows("TS"):
        code = str(r.get("TSPARMCD") or "").strip().upper()
        out.setdefault(code, []).append(_full_tsval(r))
    return out


def ts_parameters(ctx: Context) -> Iterator[Finding]:
    ts = _ts_values(ctx)
    for code, (source, getter, same) in _PARAMS.items():
        usdm_value = getter(ctx.view)
        if not usdm_value:
            continue
        values = ts.get(code)
        if not values:
            yield Finding("TC-TS-001", "info", CAT,
                          f"TS has no {code} although the protocol defines it",
                          usdm_ref=f"{source} = '{usdm_value}'",
                          sdtm_ref=f"TS.TSPARMCD='{code}'")
            continue
        if not any(same(usdm_value, v) for v in values):
            shown = " | ".join(values)
            yield Finding("TC-TS-001", "warning", CAT,
                          f"TS {code} '{shown[:120]}' does not match protocol "
                          f"value '{usdm_value[:120]}'",
                          usdm_ref=f"{source} = '{usdm_value}'",
                          sdtm_ref=f"TS.TSPARMCD='{code}' TSVAL='{shown}'")


def ts_objectives(ctx: Context) -> Iterator[Finding]:
    ts = _ts_values(ctx).get("OBJPRIM", [])
    primary = [o for o in ctx.view.objectives if o.level == "PRIMARY" and o.text]
    def agrees(usdm_text: str, ts_text: str) -> bool:
        return _text_agrees(usdm_text, ts_text, OBJECTIVE_SIMILARITY_MIN)

    for obj in primary:
        if not any(agrees(obj.text, v) for v in ts):
            best = max((text_similarity(obj.text, v) for v in ts), default=0.0)
            yield Finding("TC-TS-002", "warning", CAT,
                          f"Primary objective not found in TS OBJPRIM "
                          f"(best similarity {best:.2f}): '{obj.text[:120]}'",
                          usdm_ref=f"Objective {obj.id}",
                          sdtm_ref="TS.TSPARMCD='OBJPRIM'")
    for value in ts:
        if not any(agrees(o.text, value) for o in primary):
            best = max((text_similarity(o.text, value) for o in primary),
                       default=0.0)
            yield Finding("TC-TS-002", "warning", CAT,
                          f"TS OBJPRIM is not a protocol primary objective "
                          f"(best similarity {best:.2f}): '{value[:120]}'",
                          usdm_ref="StudyDesign.objectives (primary)",
                          sdtm_ref="TS.TSPARMCD='OBJPRIM'")


RULES: tuple[Rule, ...] = (
    Rule((RuleSpec("TC-TS-001", "TS parameters match protocol values "
                   "(TITLE, TPHASE, TBLIND, PLANSUB, REGID, SPONSOR)",
                   CAT, "warning", ("TS",)),), ts_parameters),
    Rule((RuleSpec("TC-TS-002", "TS OBJPRIM matches protocol primary objectives",
                   CAT, "warning", ("TS",)),), ts_objectives),
)
