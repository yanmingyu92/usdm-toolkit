"""Generate SDTM Trial Design domain datasets from a USDM JSON study.

Supports the USDM v4.0 JSON structure as produced by the DDF-RA API and the
``usdm`` reference package (``study.versions[*].studyDesigns[*]``).  The
mapping applied here is documented in ``docs/trial_design_mapping.md``;
assumptions are flagged in code comments with ``ASSUMPTION:``.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

DOMAIN_COLUMNS: dict[str, list[str]] = {
    "TS": ["STUDYID", "DOMAIN", "TSSEQ", "TSPARMCD", "TSPARM", "TSVAL"],
    "TA": ["STUDYID", "DOMAIN", "ARMCD", "ARM", "TAETORD", "ETCD", "ELEMENT", "EPOCH"],
    "TE": ["STUDYID", "DOMAIN", "ETCD", "ELEMENT", "TESTRL", "TEENRL"],
    "TV": ["STUDYID", "DOMAIN", "VISITNUM", "VISIT"],
    "TI": ["STUDYID", "DOMAIN", "IETESTCD", "IETEST", "IECAT"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _decode(code: Any) -> str:
    """Return the human-readable decode of a USDM Code or AliasCode."""
    if not isinstance(code, dict):
        return ""
    if code.get("instanceType") == "AliasCode":
        code = code.get("standardCode") or {}
    return code.get("decode") or code.get("code") or ""


def _short_code(name: str, used: set[str], maxlen: int = 8) -> str:
    """Derive an SDTM short code (<=8 chars, uppercase alnum) from a name.

    ASSUMPTION: USDM carries no ARMCD/ETCD equivalent, so the short code is
    derived from the name (uppercased, non-alphanumeric stripped, truncated).
    Collisions are resolved by appending a numeric suffix.
    """
    base = re.sub(r"[^A-Z0-9]", "", (name or "").upper())[:maxlen] or "X"
    code = base
    n = 1
    while code in used:
        n += 1
        code = f"{base[: maxlen - len(str(n))]}{n}"
    used.add(code)
    return code


def _chain(nodes: list[dict]) -> list[dict]:
    """Order a previousId/nextId linked list of USDM nodes.

    Nodes not reachable from the chain head(s) are appended in file order so
    that nothing is silently dropped.
    """
    by_id = {n.get("id"): n for n in nodes}
    ordered: list[dict] = []
    seen: set[str] = set()
    for start in [n for n in nodes if not n.get("previousId")] or nodes[:1]:
        cur = start
        while cur and cur.get("id") not in seen:
            ordered.append(cur)
            seen.add(cur.get("id"))
            cur = by_id.get(cur.get("nextId"))
    ordered.extend(n for n in nodes if n.get("id") not in seen)
    return ordered


# ---------------------------------------------------------------------------
# Domain builders
# ---------------------------------------------------------------------------

def _is_registry(org: dict) -> bool:
    return "registry" in _decode(org.get("type")).lower()


def _study_id(version: dict, study: dict) -> str:
    """Pick the sponsor-issued identifier as STUDYID.

    ASSUMPTION: the sponsor is the identifier-issuing organisation whose type
    decode does not mark it as a study registry (e.g. "Clinical Study
    Sponsor", "Drug Company"); if none matches, the first identifier is used.
    """
    orgs = {o.get("id"): o for o in version.get("organizations", [])}
    identifiers = version.get("studyIdentifiers", [])
    for ident in identifiers:
        org = orgs.get(ident.get("scopeId"), {})
        if org and not _is_registry(org):
            return ident.get("text") or ""
    if identifiers:
        return identifiers[0].get("text") or ""
    return study.get("name") or "UNKNOWN"


def _build_ts(study: dict, version: dict, design: dict, studyid: str) -> list[dict]:
    orgs = {o.get("id"): o for o in version.get("organizations", [])}
    sponsor, registry_id = "", ""
    for ident in version.get("studyIdentifiers", []):
        org = orgs.get(ident.get("scopeId"), {})
        if not org:
            continue
        if _is_registry(org):
            if not registry_id:
                registry_id = ident.get("text") or ""
        elif not sponsor:
            sponsor = org.get("name") or ""

    titles = version.get("titles", [])
    title = ""
    for want in ("official", "brief"):
        for t in titles:
            if want in _decode(t.get("type")).lower():
                title = t.get("text") or ""
                break
        if title:
            break
    if not title and titles:
        title = titles[0].get("text") or ""

    population = design.get("population") or {}
    enrollment = (population.get("plannedEnrollmentNumber") or {}).get("value")

    parms = [
        ("STUDYID", "Study Identifier", studyid),
        ("TITLE", "Trial Title", title),
        ("SPONSOR", "Sponsor Name", sponsor),
        ("REGID", "Registry Identifier", registry_id),
        ("PHASE", "Trial Phase Classification", _decode(design.get("studyPhase"))),
        ("INTMODEL", "Intervention Model", _decode(design.get("model"))),
        ("BLIND", "Trial Blinding Schema", _decode(design.get("blindingSchema"))),
        ("STYPE", "Study Type", _decode(design.get("studyType"))),
        ("ENROLL", "Planned Enrollment", "" if enrollment is None else str(int(enrollment))),
    ]
    return [
        {"STUDYID": studyid, "DOMAIN": "TS", "TSSEQ": i + 1,
         "TSPARMCD": cd, "TSPARM": nm, "TSVAL": val}
        for i, (cd, nm, val) in enumerate(parms)
        if val != ""
    ]


def _build_ta(design: dict, studyid: str) -> list[dict]:
    epochs = _chain(design.get("epochs", []))
    cells = {(c.get("armId"), c.get("epochId")): c
             for c in design.get("studyCells", [])}
    elements = {e.get("id"): e for e in design.get("elements", [])}
    etcd_used: set[str] = set()
    etcd = {eid: _short_code(e.get("name", ""), etcd_used)
            for eid, e in elements.items()}

    rows: list[dict] = []
    armcd_used: set[str] = set()
    for arm in design.get("arms", []):
        armcd = _short_code(arm.get("name", ""), armcd_used)
        order = 0
        for epoch in epochs:
            cell = cells.get((arm.get("id"), epoch.get("id")))
            if not cell:
                continue
            for eid in cell.get("elementIds", []):
                element = elements.get(eid)
                if not element:
                    continue
                order += 1
                rows.append({
                    "STUDYID": studyid, "DOMAIN": "TA",
                    "ARMCD": armcd, "ARM": arm.get("name") or "",
                    "TAETORD": order,
                    "ETCD": etcd[eid], "ELEMENT": element.get("name") or "",
                    "EPOCH": epoch.get("name") or "",
                })
    return rows


def _build_te(design: dict, studyid: str) -> list[dict]:
    used: set[str] = set()
    rows = []
    for element in design.get("elements", []):
        start = (element.get("transitionStartRule") or {}).get("text") or ""
        end = (element.get("transitionEndRule") or {}).get("text") or ""
        rows.append({
            "STUDYID": studyid, "DOMAIN": "TE",
            "ETCD": _short_code(element.get("name", ""), used),
            "ELEMENT": element.get("name") or "",
            "TESTRL": start, "TEENRL": end,
        })
    return rows


def _build_tv(design: dict, studyid: str) -> list[dict]:
    return [
        {"STUDYID": studyid, "DOMAIN": "TV", "VISITNUM": i + 1,
         "VISIT": enc.get("name") or ""}
        for i, enc in enumerate(_chain(design.get("encounters", [])))
    ]


def _build_ti(version: dict, design: dict, studyid: str) -> list[dict]:
    items = {it.get("id"): it for it in version.get("eligibilityCriterionItems", [])}
    rows = []
    for crit in design.get("eligibilityCriteria", []):
        cat_decode = _decode(crit.get("category")).upper()
        # ASSUMPTION: the inclusion/exclusion split is taken from the CT decode
        # of EligibilityCriterion.category.
        iecat = "EXCLUSION" if "EXCL" in cat_decode else "INCLUSION"
        ident = str(crit.get("identifier") or "").strip()
        prefix = "EXCL" if iecat == "EXCLUSION" else "INCL"
        ietestcd = f"{prefix}{ident.zfill(3)}" if ident else prefix
        item = items.get(crit.get("criterionItemId"), {})
        ietest = item.get("text") or crit.get("description") or crit.get("name") or ""
        rows.append({
            "STUDYID": studyid, "DOMAIN": "TI",
            "IETESTCD": ietestcd, "IETEST": ietest, "IECAT": iecat,
        })
    return rows


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_domains(usdm: dict) -> dict[str, list[dict]]:
    """Convert a USDM JSON study dict into SDTM Trial Design domain rows.

    Returns a mapping of domain name (``TS``, ``TA``, ``TE``, ``TV``, ``TI``)
    to a list of row dicts keyed by SDTM variable name.

    ASSUMPTION: only the first study version and its first study design are
    converted (single-design studies are the common DDF case).
    """
    study = usdm.get("study", {})
    versions = study.get("versions") or [{}]
    version = versions[0]
    designs = version.get("studyDesigns") or [{}]
    design = designs[0]

    studyid = _study_id(version, study)
    return {
        "TS": _build_ts(study, version, design, studyid),
        "TA": _build_ta(design, studyid),
        "TE": _build_te(design, studyid),
        "TV": _build_tv(design, studyid),
        "TI": _build_ti(version, design, studyid),
    }


def write_domains(domains: dict[str, list[dict]], out_dir: str | Path) -> list[Path]:
    """Write each domain to ``<out_dir>/<DOMAIN>.csv``; returns written paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for domain, rows in domains.items():
        path = out / f"{domain}.csv"
        columns = DOMAIN_COLUMNS[domain]
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        written.append(path)
    return written
