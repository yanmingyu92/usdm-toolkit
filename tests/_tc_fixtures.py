"""Synthetic USDM study + matching SDTM datasets for trace-check tests.

``consistent_usdm()`` and ``consistent_sdtm()`` describe the same study, so a
trace-check run over them must produce no error/warning findings. Tests copy
and mutate them to inject one discrepancy at a time.
"""

from __future__ import annotations

import copy


def _code(decode: str, code: str = "C1") -> dict:
    return {"id": f"Code_{code}_{decode[:4]}", "code": code,
            "codeSystem": "http://www.cdisc.org", "codeSystemVersion": "2025",
            "decode": decode, "instanceType": "Code"}


def _alias(decode: str, code: str = "C2") -> dict:
    return {"id": f"Alias_{code}", "standardCode": _code(decode, code),
            "standardCodeAliases": [], "instanceType": "AliasCode"}


def _chain(prefix: str, specs: list[tuple[str, str]], **extra) -> list[dict]:
    """Build a previousId/nextId chain of ``(name, label)`` items."""
    out = []
    for i, (name, label) in enumerate(specs, start=1):
        out.append({
            "id": f"{prefix}_{i}", "name": name, "label": label,
            "previousId": f"{prefix}_{i - 1}" if i > 1 else None,
            "nextId": f"{prefix}_{i + 1}" if i < len(specs) else None,
            **extra,
        })
    return out


def _bc(idx: int, name: str, code: str) -> dict:
    return {"id": f"BiomedicalConcept_{idx}", "name": name, "label": name,
            "code": _alias(name, code), "properties": [],
            "instanceType": "BiomedicalConcept"}


def consistent_usdm() -> dict:
    epochs = _chain("StudyEpoch", [("EP1", "Screening"), ("EP2", "Treatment")],
                    instanceType="StudyEpoch")
    encounters = _chain("Encounter", [("E1", "Screening"), ("E2", "Week 2")],
                        instanceType="Encounter")
    elements = [
        {"id": "StudyElement_1", "name": "EL1", "label": "Screen",
         "instanceType": "StudyElement"},
        {"id": "StudyElement_2", "name": "EL2", "label": "Placebo",
         "instanceType": "StudyElement"},
        {"id": "StudyElement_3", "name": "EL3", "label": "Drug",
         "instanceType": "StudyElement"},
    ]
    cells = []
    for arm, treat_el in (("StudyArm_1", "StudyElement_2"),
                          ("StudyArm_2", "StudyElement_3")):
        cells.append({"armId": arm, "epochId": "StudyEpoch_1",
                      "elementIds": ["StudyElement_1"]})
        cells.append({"armId": arm, "epochId": "StudyEpoch_2",
                      "elementIds": [treat_el]})
    timeline = {
        "id": "ScheduleTimeline_1", "name": "Main", "mainTimeline": True,
        "instances": [
            {"id": "SAI_1", "encounterId": "Encounter_1",
             "activityIds": ["Activity_1", "Activity_2"],
             "instanceType": "ScheduledActivityInstance"},
            {"id": "SAI_2", "encounterId": "Encounter_2",
             "activityIds": ["Activity_1"],
             "instanceType": "ScheduledActivityInstance"},
        ],
    }
    return {
        "usdmVersion": "4.0.0",
        "study": {"id": "Study_1", "name": "SYNTH", "versions": [{
            "id": "StudyVersion_1",
            "studyIdentifiers": [
                {"id": "SI_1", "text": "SYN-001", "scopeId": "Org_1"},
                {"id": "SI_2", "text": "NCT00000001", "scopeId": "Org_2"},
            ],
            "organizations": [
                {"id": "Org_1", "name": "ACME", "type": _code("Sponsor")},
                {"id": "Org_2", "name": "CT-GOV",
                 "type": _code("Study Registry")},
            ],
            "titles": [{"id": "T1", "text": "A Synthetic Study of Drugamab",
                        "type": _code("Official Study Title")}],
            "studyInterventions": [
                {"id": "SIV_1", "name": "DRUGAMAB", "label": "Drugamab"},
                {"id": "SIV_2", "name": "PLACEBO", "label": "Placebo"},
            ],
            "eligibilityCriterionItems": [
                {"id": "ECI_1", "text": "<p>Age at least 18 years</p>"},
                {"id": "ECI_2", "text": "Pregnant or breastfeeding"},
            ],
            "biomedicalConcepts": [
                _bc(1, "Systolic Blood Pressure", "C25298"),
                _bc(2, "Body Weight", "C25208"),
            ],
            "studyDesigns": [{
                "id": "Design_1", "name": "Design 1",
                "studyPhase": _alias("Phase II Trial", "C15601"),
                "blindingSchema": _alias("Double Blind Study", "C15228"),
                "population": {"plannedEnrollmentNumber": {"value": 60.0}},
                "arms": [
                    {"id": "StudyArm_1", "name": "Placebo", "label": "Placebo"},
                    {"id": "StudyArm_2", "name": "Drugamab 10 mg",
                     "label": "Drugamab 10 mg"},
                ],
                "epochs": epochs, "elements": elements, "studyCells": cells,
                "encounters": encounters,
                "eligibilityCriteria": [
                    {"id": "EC_1", "identifier": "01",
                     "category": _code("Inclusion Criteria"),
                     "criterionItemId": "ECI_1"},
                    {"id": "EC_2", "identifier": "02",
                     "category": _code("Exclusion Criteria"),
                     "criterionItemId": "ECI_2"},
                ],
                "objectives": [
                    {"id": "OBJ_1", "name": "OBJ1",
                     "text": "To compare blood pressure lowering of Drugamab "
                             "versus placebo",
                     "level": _code("Study Primary Objective")},
                ],
                "activities": [
                    {"id": "Activity_1", "name": "Vitals",
                     "biomedicalConceptIds": ["BiomedicalConcept_1"]},
                    {"id": "Activity_2", "name": "Weight",
                     "biomedicalConceptIds": ["BiomedicalConcept_2"]},
                ],
                "scheduleTimelines": [timeline],
            }],
        }]},
    }


def _rows(domain: str, rows: list[dict]) -> tuple[dict, ...]:
    return tuple({"STUDYID": "SYN-001", "DOMAIN": domain, **r} for r in rows)


def consistent_sdtm() -> dict[str, tuple[dict, ...]]:
    arms = (("PBO", "Placebo", "PBO", "Placebo"),
            ("DRG10", "Drugamab 10 mg", "DRG", "Drug"))
    ta, dm, se, sv, vs = [], [], [], [], []
    for armcd, arm, etcd, element in arms:
        ta.append({"ARMCD": armcd, "ARM": arm, "TAETORD": 1, "ETCD": "SCRN",
                   "ELEMENT": "Screen", "EPOCH": "SCREENING"})
        ta.append({"ARMCD": armcd, "ARM": arm, "TAETORD": 2, "ETCD": etcd,
                   "ELEMENT": element, "EPOCH": "TREATMENT"})
        subj = f"SYN-001-{armcd}"
        dm.append({"USUBJID": subj, "ARMCD": armcd, "ARM": arm,
                   "ACTARMCD": armcd, "ACTARM": arm})
        se.append({"USUBJID": subj, "ETCD": "SCRN", "ELEMENT": "Screen"})
        se.append({"USUBJID": subj, "ETCD": etcd, "ELEMENT": element})
        for num, visit in ((1, "SCREENING"), (2, "WEEK 2")):
            sv.append({"USUBJID": subj, "VISITNUM": num, "VISIT": visit})
            vs.append({"USUBJID": subj, "VSTESTCD": "SYSBP", "VISITNUM": num,
                       "VISIT": visit})
        vs.append({"USUBJID": subj, "VSTESTCD": "WEIGHT", "VISITNUM": 1,
                   "VISIT": "SCREENING"})
    return {
        "TA": _rows("TA", ta),
        "TE": _rows("TE", [
            {"ETCD": "SCRN", "ELEMENT": "Screen"},
            {"ETCD": "PBO", "ELEMENT": "Placebo"},
            {"ETCD": "DRG", "ELEMENT": "Drug"},
        ]),
        "TV": _rows("TV", [{"VISITNUM": 1, "VISIT": "SCREENING"},
                           {"VISITNUM": 2, "VISIT": "WEEK 2"}]),
        "TI": _rows("TI", [
            {"IETESTCD": "INCL01", "IETEST": "Age at least 18 years",
             "IECAT": "INCLUSION"},
            {"IETESTCD": "EXCL02", "IETEST": "Pregnant or breastfeeding",
             "IECAT": "EXCLUSION"},
        ]),
        "TS": _rows("TS", [
            {"TSPARMCD": "TITLE", "TSVAL": "A Synthetic Study of Drugamab"},
            {"TSPARMCD": "TPHASE", "TSVAL": "Phase II Trial"},
            {"TSPARMCD": "TBLIND", "TSVAL": "DOUBLE BLIND"},
            {"TSPARMCD": "PLANSUB", "TSVAL": "60"},
            {"TSPARMCD": "REGID", "TSVAL": "NCT00000001"},
            {"TSPARMCD": "OBJPRIM", "TSVAL": "To compare blood pressure "
                                             "lowering of Drugamab versus placebo"},
        ]),
        "DM": _rows("DM", dm),
        "SE": _rows("SE", se),
        "SV": _rows("SV", sv),
        "EX": _rows("EX", [{"USUBJID": "SYN-001-DRG10", "EXTRT": "DRUGAMAB"},
                           {"USUBJID": "SYN-001-PBO", "EXTRT": "PLACEBO"}]),
        "VS": _rows("VS", vs),
    }


def mutate_rows(sdtm: dict, domain: str, fn) -> dict:
    """Return a copy of ``sdtm`` with ``fn(rows) -> rows`` applied to a domain."""
    out = dict(sdtm)
    out[domain] = tuple(fn([dict(r) for r in sdtm[domain]]))
    return out


def deep(usdm: dict) -> dict:
    return copy.deepcopy(usdm)


def design(usdm: dict) -> dict:
    return usdm["study"]["versions"][0]["studyDesigns"][0]


def version(usdm: dict) -> dict:
    return usdm["study"]["versions"][0]
