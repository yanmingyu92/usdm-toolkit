"""A flat, read-only view of the parts of a USDM study that trace-check uses.

Only the first study version and its first study design are read (same
ASSUMPTION as ``trial_design.generator``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..trial_design.generator import _chain, _decode, _is_registry
from .usdm_text import TextResolver, strip_markup


@dataclass(frozen=True)
class Item:
    """A USDM object as seen by matching: id, display text and aliases."""

    id: str
    display: str
    aliases: tuple[str, ...]

    def label_item(self) -> tuple[str, tuple[str, ...]]:
        return (self.display, self.aliases)


@dataclass(frozen=True)
class Criterion:
    id: str
    category: str          # INCLUSION | EXCLUSION
    number: int | None
    text: str


@dataclass(frozen=True)
class Objective:
    id: str
    level: str             # PRIMARY | SECONDARY | OTHER
    text: str


@dataclass(frozen=True)
class PlannedBC:
    encounter_id: str
    activity_id: str
    bc_id: str
    bc_code: str
    bc_name: str


@dataclass(frozen=True)
class StudyView:
    arms: tuple[Item, ...] = ()
    epochs: tuple[Item, ...] = ()
    elements: tuple[Item, ...] = ()
    encounters: tuple[Item, ...] = ()
    treatments: tuple[Item, ...] = ()
    arm_paths: dict[str, tuple[str, ...]] = field(default_factory=dict)
    criteria: tuple[Criterion, ...] = ()
    objectives: tuple[Objective, ...] = ()
    soa: tuple[PlannedBC, ...] = ()
    title: str = ""
    sponsor_name: str = ""
    registry_id: str = ""
    phase: str = ""
    blinding: str = ""
    planned_enrollment: int | None = None

    @classmethod
    def from_usdm(cls, usdm: dict) -> StudyView:
        study = usdm.get("study") if isinstance(usdm.get("study"), dict) else {}
        version = (_lst(study, "versions") or [{}])[0]
        design = (_lst(version, "studyDesigns") or [{}])[0]
        elements = {e.get("id"): e for e in _lst(design, "elements")}
        sponsor, registry = _sponsor_and_registry(version)
        text = TextResolver(usdm)
        return cls(
            arms=_items(_lst(design, "arms")),
            epochs=_items(_chain(_lst(design, "epochs"))),
            elements=_items(_lst(design, "elements")),
            encounters=_items(_chain(_lst(design, "encounters"))),
            treatments=_items(_lst(version, "studyInterventions")
                              + _lst(version, "administrableProducts")),
            arm_paths=_arm_paths(design, elements),
            criteria=_criteria(version, design, text),
            objectives=_objectives(design, text),
            soa=_soa(version, design),
            title=_title(version),
            sponsor_name=sponsor,
            registry_id=registry,
            phase=_decode(design.get("studyPhase")),
            blinding=_decode(design.get("blindingSchema")),
            planned_enrollment=_enrollment(design),
        )

    def encounter(self, encounter_id: str) -> Item | None:
        return next((e for e in self.encounters if e.id == encounter_id), None)


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------


def _lst(obj: Any, key: str) -> list[dict]:
    """``obj[key]`` as a list of dicts; null, scalars and non-dict items dropped."""
    value = obj.get(key) if isinstance(obj, dict) else None
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def _ids(obj: Any, key: str) -> list[str]:
    """``obj[key]`` as a list of id strings."""
    value = obj.get(key) if isinstance(obj, dict) else None
    return [x for x in value if isinstance(x, str)] if isinstance(value, list) else []

def plain_text(text: Any) -> str:
    """Strip XHTML / usdm:ref tags and collapse whitespace (no resolution)."""
    return strip_markup(text)


def _display(obj: dict) -> str:
    return plain_text(obj.get("label") or obj.get("name") or obj.get("id"))


def _items(objs: list[dict]) -> tuple[Item, ...]:
    out = []
    for o in objs:
        aliases = tuple(dict.fromkeys(
            plain_text(v) for v in (o.get("label"), o.get("name")) if v))
        out.append(Item(str(o.get("id") or ""), _display(o), aliases))
    return tuple(out)


def _arm_paths(design: dict, elements: dict) -> dict[str, tuple[str, ...]]:
    """Per arm, the element labels in epoch order; repeats collapsed."""
    cells = {(c.get("armId"), c.get("epochId")): c
             for c in _lst(design, "studyCells")}
    epochs = _chain(_lst(design, "epochs"))
    paths = {}
    for arm in _lst(design, "arms"):
        seq: list[str] = []
        for epoch in epochs:
            cell = cells.get((arm.get("id"), epoch.get("id"))) or {}
            for eid in _ids(cell, "elementIds"):
                label = _display(elements.get(eid) or {"id": eid})
                if not seq or seq[-1] != label:
                    seq.append(label)
        paths[arm.get("id")] = tuple(seq)
    return paths


def _criteria(version: dict, design: dict,
              text: TextResolver) -> tuple[Criterion, ...]:
    items = {i.get("id"): i for i in _lst(version, "eligibilityCriterionItems")}
    out = []
    for c in _lst(design, "eligibilityCriteria"):
        cat = "EXCLUSION" if "EXCL" in _decode(c.get("category")).upper() \
            else "INCLUSION"
        digits = re.sub(r"\D", "", str(c.get("identifier") or ""))
        item = items.get(c.get("criterionItemId")) or {}
        raw = item.get("text") or c.get("text") or c.get("description") \
            or c.get("name") or ""
        out.append(Criterion(str(c.get("id")), cat,
                             int(digits) if digits else None,
                             text.plain(raw, item.get("dictionaryId"))))
    return tuple(out)


def _objectives(design: dict, text: TextResolver) -> tuple[Objective, ...]:
    out = []
    for o in _lst(design, "objectives"):
        level = _decode(o.get("level")).upper()
        tag = "PRIMARY" if "PRIMARY" in level else (
            "SECONDARY" if "SECONDARY" in level else "OTHER")
        out.append(Objective(str(o.get("id")), tag,
                             text.plain(o.get("text"), o.get("dictionaryId"))))
    return tuple(out)


def _bc_code(bc: dict) -> str:
    code = bc.get("code") or {}
    if code.get("instanceType") == "AliasCode" or "standardCode" in code:
        code = code.get("standardCode") or {}
    return str(code.get("code") or "")


def _soa(version: dict, design: dict) -> tuple[PlannedBC, ...]:
    """BCs planned at each encounter, read from every schedule timeline.

    ASSUMPTION: only instances with an ``encounterId`` count; activities that
    point to a sub-timeline contribute their own BCs at that encounter.
    """
    bcs = {b.get("id"): b for b in _lst(version, "biomedicalConcepts")}
    acts = {a.get("id"): a for a in _lst(design, "activities")}
    seen: dict[tuple[str, str], PlannedBC] = {}
    for timeline in _lst(design, "scheduleTimelines"):
        for inst in _lst(timeline, "instances"):
            enc = inst.get("encounterId")
            if not enc:
                continue
            for aid in _ids(inst, "activityIds"):
                for bid in _ids(acts.get(aid), "biomedicalConceptIds"):
                    bc = bcs.get(bid)
                    if bc is None:
                        continue
                    key = (enc, bid)
                    seen.setdefault(key, PlannedBC(
                        enc, aid, bid, _bc_code(bc),
                        plain_text(bc.get("label") or bc.get("name"))))
    return tuple(seen.values())


def _sponsor_and_registry(version: dict) -> tuple[str, str]:
    orgs = {o.get("id"): o for o in _lst(version, "organizations")}
    sponsor = registry = ""
    for ident in _lst(version, "studyIdentifiers"):
        org = orgs.get(ident.get("scopeId")) or {}
        if not org:
            continue
        if _is_registry(org):
            registry = registry or str(ident.get("text") or "")
        else:
            sponsor = sponsor or str(org.get("name") or "")
    return sponsor, registry


def _title(version: dict) -> str:
    titles = _lst(version, "titles")
    for want in ("official", "public", "brief"):
        for t in titles:
            if want in _decode(t.get("type")).lower():
                return plain_text(t.get("text"))
    return plain_text(titles[0].get("text")) if titles else ""


def _enrollment(design: dict) -> int | None:
    value = ((design.get("population") or {})
             .get("plannedEnrollmentNumber") or {}).get("value")
    try:
        return None if value is None else int(float(value))
    except (TypeError, ValueError):
        return None
