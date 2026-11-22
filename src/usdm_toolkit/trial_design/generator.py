"""Generate SDTM Trial Design domain datasets from a USDM JSON study.

Supports the USDM v4.0 JSON structure as produced by the DDF-RA API and the
``usdm`` reference package (``study.versions[*].studyDesigns[*]``).  The
mapping applied here is documented in ``docs/trial_design_mapping.md``;
assumptions are flagged in code comments with ``ASSUMPTION:``.
"""

from __future__ import annotations

import csv
import math
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

# TS parameters written, in output order: (TSPARMCD, TSPARM).
# Source: CDISC SDTM Controlled Terminology 2026-09-25 (NCI EVS), codelists
# TSPARMCD (C66738) and TSPARM (C67152). NCI codes of the terms: TITLE C49802,
# SPONSOR C70793, REGID C98714, TPHASE C48281, INTMODEL C98746,
# TBLIND C49658, STYPE C142175, PLANSUB C49692.
# STUDYID is a column of every TS row, not a TS parameter.
TS_PARAMETERS: list[tuple[str, str]] = [
    ("TITLE", "Trial Title"),
    ("SPONSOR", "Clinical Study Sponsor"),
    ("REGID", "Registry Identifier"),
    ("TPHASE", "Trial Phase Classification"),
    ("INTMODEL", "Intervention Model"),
    ("TBLIND", "Trial Blinding Schema"),
    ("STYPE", "Study Type"),
    ("PLANSUB", "Planned Number of Subjects"),
]


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

    ASSUMPTION: USDM carries no ARMCD/ETCD equivalent, so unless the study
    states one as an extension attribute (see ``_ext``) the short code is
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


def _ext(node: dict, name: str) -> str:
    """Return the value of the node's extension attribute ``name``, or "".

    USDM v4.0 has no attribute for ARMCD, ETCD or VISITNUM. A study
    definition may carry the values the protocol states as an
    ``ExtensionAttribute`` (``valueString``) whose ``url`` ends with
    ``/ARMCD``, ``/ETCD`` or ``/VISITNUM`` (only the last path segment is
    matched, case-insensitively). They are used when present; the
    derivation otherwise.
    """
    for ext in node.get("extensionAttributes") or []:
        if str(ext.get("url", "")).rstrip("/").upper().endswith("/" + name) and ext.get("valueString"):
            return str(ext["valueString"])
    return ""


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


def _build_ts(study: dict, version: dict, design: dict,
              studyid: str) -> tuple[list[dict], list[dict]]:
    orgs = {o.get("id"): o for o in version.get("organizations", [])}
    sponsor, registry_id = "", ""
    sponsor_org: dict = {}
    registry_ident: dict = {}
    for ident in version.get("studyIdentifiers", []):
        org = orgs.get(ident.get("scopeId"), {})
        if not org:
            continue
        if _is_registry(org):
            if not registry_id:
                registry_id = ident.get("text") or ""
                registry_ident = ident
        elif not sponsor:
            sponsor = org.get("name") or ""
            sponsor_org = org

    titles = version.get("titles", [])
    title = ""
    title_node: dict = {}
    for want in ("official", "brief"):
        for t in titles:
            if want in _decode(t.get("type")).lower():
                title = t.get("text") or ""
                title_node = t
                break
        if title:
            break
    if not title and titles:
        title = titles[0].get("text") or ""
        title_node = titles[0]

    population = design.get("population") or {}
    quantity = population.get("plannedEnrollmentNumber") or {}
    enrollment = quantity.get("value")

    values = {
        "TITLE": title,
        "SPONSOR": sponsor,
        "REGID": registry_id,
        "TPHASE": _decode(design.get("studyPhase")),
        "INTMODEL": _decode(design.get("model")),
        "TBLIND": _decode(design.get("blindingSchema")),
        "STYPE": _decode(design.get("studyType")),
        "PLANSUB": "" if enrollment is None else str(int(enrollment)),
    }
    # ASSUMPTION: TSVAL is the USDM decode, i.e. the NCI preferred term
    # (e.g. "Double Blind Study"), not the CDISC submission value
    # ("DOUBLE BLIND"); mapping one to the other needs the CT itself.
    def code_source(attr: str) -> tuple[dict, str]:
        node = design.get(attr)
        return (node if isinstance(node, dict) else {}), f"{design.get('id')}.{attr}"

    # Per parameter: (the instance that holds the value, "<owner id>.<attribute>").
    sources = {
        "TITLE": (title_node, f"{title_node.get('id')}.text"),
        "SPONSOR": (sponsor_org, f"{sponsor_org.get('id')}.name"),
        "REGID": (registry_ident, f"{registry_ident.get('id')}.text"),
        "TPHASE": code_source("studyPhase"),
        "INTMODEL": code_source("model"),
        "TBLIND": code_source("blindingSchema"),
        "STYPE": code_source("studyType"),
        "PLANSUB": (quantity, f"{population.get('id')}.plannedEnrollmentNumber"),
    }

    rows: list[dict] = []
    srcs: list[dict] = []
    seq: dict[str, int] = {}
    for cd, nm in TS_PARAMETERS:
        val = values[cd]
        if val == "":
            continue
        # TSSEQ numbers the values of one parameter (1, 2, ... per TSPARMCD).
        seq[cd] = seq.get(cd, 0) + 1
        rows.append({"STUDYID": studyid, "DOMAIN": "TS", "TSSEQ": seq[cd],
                     "TSPARMCD": cd, "TSPARM": nm, "TSVAL": val})
        node, attribute = sources[cd]
        srcs.append({"usdm_ids": [node.get("id")], "usdm_attribute": attribute})
    return rows, srcs


def _build_ta(design: dict, studyid: str) -> tuple[list[dict], list[dict]]:
    epochs = _chain(design.get("epochs", []))
    cells = {(c.get("armId"), c.get("epochId")): c
             for c in design.get("studyCells", [])}
    elements = {e.get("id"): e for e in design.get("elements", [])}
    etcd_used: set[str] = set()
    etcd_used.update(_ext(e, "ETCD") for e in elements.values() if _ext(e, "ETCD"))
    etcd = {eid: _ext(e, "ETCD") or _short_code(e.get("name", ""), etcd_used)
            for eid, e in elements.items()}

    rows: list[dict] = []
    srcs: list[dict] = []
    armcd_used: set[str] = {_ext(a, "ARMCD") for a in design.get("arms", []) if _ext(a, "ARMCD")}
    for arm in design.get("arms", []):
        armcd = _ext(arm, "ARMCD") or _short_code(arm.get("name", ""), armcd_used)
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
                srcs.append({"usdm_ids": [arm.get("id"), epoch.get("id"),
                                          cell.get("id"), eid]})
    return rows, srcs


def _build_te(design: dict, studyid: str) -> tuple[list[dict], list[dict]]:
    used: set[str] = {_ext(e, "ETCD") for e in design.get("elements", []) if _ext(e, "ETCD")}
    rows: list[dict] = []
    srcs: list[dict] = []
    for element in design.get("elements", []):
        start = (element.get("transitionStartRule") or {}).get("text") or ""
        end = (element.get("transitionEndRule") or {}).get("text") or ""
        rows.append({
            "STUDYID": studyid, "DOMAIN": "TE",
            "ETCD": _ext(element, "ETCD") or _short_code(element.get("name", ""), used),
            "ELEMENT": element.get("name") or "",
            "TESTRL": start, "TEENRL": end,
        })
        srcs.append({"usdm_ids": [element.get("id")]})
    return rows, srcs


def _build_tv(design: dict, studyid: str) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    srcs: list[dict] = []
    for i, enc in enumerate(_chain(design.get("encounters", []))):
        stated = _ext(enc, "VISITNUM")
        try:
            visitnum = float(stated) if stated else i + 1
        except ValueError:
            visitnum = i + 1
        if not math.isfinite(visitnum):  # "nan", "inf"
            visitnum = i + 1
        if isinstance(visitnum, float) and visitnum.is_integer():
            visitnum = int(visitnum)
        rows.append({"STUDYID": studyid, "DOMAIN": "TV", "VISITNUM": visitnum,
                     "VISIT": enc.get("name") or ""})
        srcs.append({"usdm_ids": [enc.get("id")]})
    return rows, srcs


def _build_ti(version: dict, design: dict,
              studyid: str) -> tuple[list[dict], list[dict]]:
    items = {it.get("id"): it for it in version.get("eligibilityCriterionItems", [])}
    rows: list[dict] = []
    srcs: list[dict] = []
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
        ids = [crit.get("id")]
        if item:
            ids.append(item.get("id"))
        srcs.append({"usdm_ids": ids})
    return rows, srcs


def _id_counts(node: Any, counts: dict[str, int] | None = None) -> dict[str, int]:
    """Count how often each ``id`` occurs on a USDM instance in the document."""
    counts = {} if counts is None else counts
    if isinstance(node, dict):
        ident = node.get("id")
        if isinstance(ident, str) and ident and "instanceType" in node:
            counts[ident] = counts.get(ident, 0) + 1
        for value in node.values():
            _id_counts(value, counts)
    elif isinstance(node, list):
        for value in node:
            _id_counts(value, counts)
    return counts


def _settle(src: dict, counts: dict[str, int]) -> dict:
    """Keep a row's ids only if each one names exactly one instance.

    A missing id, or an id that more than one instance in the document
    carries, does not identify a source: the row then gets no ids (and, for
    TS, no attribute) rather than a guess.
    """
    ids = src["usdm_ids"]
    if ids and all(isinstance(i, str) and counts.get(i) == 1 for i in ids):
        return src
    settled = {**src, "usdm_ids": []}
    if "usdm_attribute" in settled:
        settled["usdm_attribute"] = None
    return settled


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
    return generate_domains_with_sources(usdm)[0]


def generate_domains_with_sources(
    usdm: dict,
) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Like ``generate_domains``, plus the USDM instances each row came from.

    Returns ``(domains, sources)``. ``domains`` is exactly what
    ``generate_domains`` returns. ``sources`` has the same keys, and
    ``sources[domain][i]`` belongs to ``domains[domain][i]``:

    - every entry has ``usdm_ids``, a list of USDM instance ids recorded
      while the row is built (never matched afterwards by name or value):
      TA ``[arm, epoch, cell, element]``; TE ``[element]``;
      TV ``[encounter]``; TI ``[criterion, criterion item]`` (the item only
      when the criterion references one that exists); TS ``[instance that
      holds the value]`` (StudyTitle, Organization, StudyIdentifier, the
      Code/AliasCode, or the Quantity);
    - TS entries also have ``usdm_attribute``, ``"<owner id>.<attribute>"``,
      e.g. ``"InterventionalStudyDesign_1.studyPhase"``.

    A row whose source has no id, or an id that more than one instance in
    the document carries, gets ``usdm_ids == []`` (and, for TS,
    ``usdm_attribute is None``).
    """
    study = usdm.get("study", {})
    versions = study.get("versions") or [{}]
    version = versions[0]
    designs = version.get("studyDesigns") or [{}]
    design = designs[0]

    studyid = _study_id(version, study)
    built = {
        "TS": _build_ts(study, version, design, studyid),
        "TA": _build_ta(design, studyid),
        "TE": _build_te(design, studyid),
        "TV": _build_tv(design, studyid),
        "TI": _build_ti(version, design, studyid),
    }
    counts = _id_counts(usdm)
    domains = {d: rows for d, (rows, _) in built.items()}
    sources = {d: [_settle(s, counts) for s in srcs]
               for d, (_, srcs) in built.items()}
    return domains, sources


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
