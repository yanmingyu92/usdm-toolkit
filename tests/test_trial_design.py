"""Tests for the trial_design module (USDM JSON -> SDTM Trial Design CSVs)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from usdm_toolkit.trial_design import (
    generate_domains,
    generate_domains_with_sources,
    write_domains,
)

EXAMPLES_DIR = Path(__file__).parent.parent / "data" / "examples"


def _code(decode: str, code: str = "C1") -> dict:
    return {"id": f"Code_{code}", "code": code,
            "codeSystem": "http://www.cdisc.org", "codeSystemVersion": "2025",
            "decode": decode, "instanceType": "Code"}


def _alias_code(decode: str, code: str = "C2") -> dict:
    return {"id": f"AliasCode_{code}", "standardCode": _code(decode, code),
            "standardCodeAliases": [], "instanceType": "AliasCode"}


def _fixture() -> dict:
    """Minimal synthetic USDM v4-style study."""
    return {
        "usdmVersion": "4.0.0",
        "study": {
            "id": "Study_1", "name": "SYNTH", "instanceType": "Study",
            "versions": [{
                "id": "StudyVersion_1", "versionIdentifier": "1",
                "rationale": "test", "instanceType": "StudyVersion",
                "studyIdentifiers": [
                    {"id": "StudyIdentifier_1", "text": "NCT00000001",
                     "scopeId": "Organization_1", "instanceType": "StudyIdentifier"},
                    {"id": "StudyIdentifier_2", "text": "SYNTH-001",
                     "scopeId": "Organization_2", "instanceType": "StudyIdentifier"},
                ],
                "organizations": [
                    {"id": "Organization_1", "name": "CT-GOV",
                     "identifier": "CT-GOV", "identifierScheme": "USGOV",
                     "type": _code("Study Registry", "C10"),
                     "instanceType": "Organization"},
                    {"id": "Organization_2", "name": "ACME",
                     "identifier": "ACME", "identifierScheme": "DUNS",
                     "type": _code("Clinical Study Sponsor", "C11"),
                     "instanceType": "Organization"},
                ],
                "titles": [
                    {"id": "StudyTitle_1", "text": "Synthetic Study",
                     "type": _code("Official Study Title", "C12"),
                     "instanceType": "StudyTitle"},
                ],
                "eligibilityCriterionItems": [
                    {"id": "EligibilityCriterionItem_1",
                     "text": "Age >= 18 years",
                     "instanceType": "EligibilityCriterionItem"},
                    {"id": "EligibilityCriterionItem_2",
                     "text": "Pregnancy",
                     "instanceType": "EligibilityCriterionItem"},
                ],
                "studyDesigns": [{
                    "id": "InterventionalStudyDesign_1",
                    "name": "Design 1", "rationale": "test",
                    "instanceType": "InterventionalStudyDesign",
                    "studyType": _code("Interventional Study", "C20"),
                    "studyPhase": _alias_code("Phase II Trial", "C21"),
                    "model": _code("Parallel Study", "C22"),
                    "blindingSchema": _alias_code("Double Blind Study", "C23"),
                    "population": {
                        "id": "StudyDesignPopulation_1", "name": "POP",
                        "includesHealthySubjects": False,
                        "plannedEnrollmentNumber": {"id": "Quantity_1", "value": 60.0,
                                                    "instanceType": "Quantity"},
                        "instanceType": "StudyDesignPopulation",
                    },
                    "arms": [
                        {"id": "StudyArm_1", "name": "Placebo",
                         "type": _code("Placebo Comparator Arm", "C30"),
                         "instanceType": "StudyArm"},
                        {"id": "StudyArm_2", "name": "Treatment",
                         "type": _code("Experimental Arm", "C31"),
                         "instanceType": "StudyArm"},
                    ],
                    "epochs": [
                        {"id": "StudyEpoch_1", "name": "Screening",
                         "type": _code("Screening Epoch", "C40"),
                         "previousId": None, "nextId": "StudyEpoch_2",
                         "instanceType": "StudyEpoch"},
                        {"id": "StudyEpoch_2", "name": "Treatment",
                         "type": _code("Treatment Epoch", "C41"),
                         "previousId": "StudyEpoch_1", "nextId": None,
                         "instanceType": "StudyEpoch"},
                    ],
                    "elements": [
                        {"id": "StudyElement_1", "name": "Screening",
                         "transitionStartRule": {"id": "TR1", "text": "Consent",
                                                 "instanceType": "TransitionRule"},
                         "instanceType": "StudyElement"},
                        {"id": "StudyElement_2", "name": "Placebo Infusion",
                         "instanceType": "StudyElement"},
                        {"id": "StudyElement_3", "name": "Drug Infusion",
                         "instanceType": "StudyElement"},
                    ],
                    "studyCells": [
                        {"id": "StudyCell_1", "armId": "StudyArm_1",
                         "epochId": "StudyEpoch_1", "elementIds": ["StudyElement_1"],
                         "instanceType": "StudyCell"},
                        {"id": "StudyCell_2", "armId": "StudyArm_1",
                         "epochId": "StudyEpoch_2", "elementIds": ["StudyElement_2"],
                         "instanceType": "StudyCell"},
                        {"id": "StudyCell_3", "armId": "StudyArm_2",
                         "epochId": "StudyEpoch_1", "elementIds": ["StudyElement_1"],
                         "instanceType": "StudyCell"},
                        {"id": "StudyCell_4", "armId": "StudyArm_2",
                         "epochId": "StudyEpoch_2", "elementIds": ["StudyElement_3"],
                         "instanceType": "StudyCell"},
                    ],
                    "encounters": [
                        {"id": "Encounter_1", "name": "Visit 1",
                         "type": _code("Visit", "C50"),
                         "previousId": None, "nextId": "Encounter_2",
                         "instanceType": "Encounter"},
                        {"id": "Encounter_2", "name": "Visit 2",
                         "type": _code("Visit", "C51"),
                         "previousId": "Encounter_1", "nextId": None,
                         "instanceType": "Encounter"},
                    ],
                    "eligibilityCriteria": [
                        {"id": "EligibilityCriterion_1", "name": "Age",
                         "identifier": "1",
                         "category": _code("Inclusion Criteria", "C60"),
                         "criterionItemId": "EligibilityCriterionItem_1",
                         "instanceType": "EligibilityCriterion"},
                        {"id": "EligibilityCriterion_2", "name": "Pregnancy",
                         "identifier": "2",
                         "category": _code("Exclusion Criteria", "C61"),
                         "criterionItemId": "EligibilityCriterionItem_2",
                         "instanceType": "EligibilityCriterion"},
                    ],
                }],
            }],
        },
    }


@pytest.fixture()
def domains():
    return generate_domains(_fixture())


class TestSyntheticFixture:
    def test_all_domains_present(self, domains):
        assert set(domains) == {"TS", "TA", "TE", "TV", "TI"}

    def test_studyid_is_sponsor_identifier(self, domains):
        assert all(r["STUDYID"] == "SYNTH-001" for r in domains["TS"])

    def test_ts_contents(self, domains):
        ts = {r["TSPARMCD"]: r["TSVAL"] for r in domains["TS"]}
        assert ts["TITLE"] == "Synthetic Study"
        assert ts["SPONSOR"] == "ACME"
        assert ts["REGID"] == "NCT00000001"
        assert ts["TPHASE"] == "Phase II Trial"         # AliasCode -> standardCode
        assert ts["INTMODEL"] == "Parallel Study"
        assert ts["TBLIND"] == "Double Blind Study"
        assert ts["STYPE"] == "Interventional Study"
        assert ts["PLANSUB"] == "60"

    def test_ts_parameter_codes_are_sdtm_ct(self, domains):
        # TSPARMCD/TSPARM terms of SDTM CT 2026-09-25 (C66738/C67152).
        assert [(r["TSPARMCD"], r["TSPARM"]) for r in domains["TS"]] == [
            ("TITLE", "Trial Title"),
            ("SPONSOR", "Clinical Study Sponsor"),
            ("REGID", "Registry Identifier"),
            ("TPHASE", "Trial Phase Classification"),
            ("INTMODEL", "Intervention Model"),
            ("TBLIND", "Trial Blinding Schema"),
            ("STYPE", "Study Type"),
            ("PLANSUB", "Planned Number of Subjects"),
        ]

    def test_ts_has_no_studyid_parameter(self, domains):
        assert "STUDYID" not in {r["TSPARMCD"] for r in domains["TS"]}

    def test_tsseq_counts_per_parameter(self):
        usdm = _fixture()
        version = usdm["study"]["versions"][0]
        version["organizations"] = [  # no registry -> REGID is empty
            o for o in version["organizations"] if o["id"] != "Organization_1"]
        version["studyIdentifiers"] = version["studyIdentifiers"][1:]
        ts = generate_domains(usdm)["TS"]
        assert "REGID" not in {r["TSPARMCD"] for r in ts}
        # One value per parameter: every TSSEQ is 1, no gap left by REGID.
        assert [r["TSSEQ"] for r in ts] == [1] * len(ts)

    def test_ta_rows(self, domains):
        ta = domains["TA"]
        assert len(ta) == 4  # 2 arms x 2 epochs x 1 element each
        placebo = [r for r in ta if r["ARM"] == "Placebo"]
        assert [r["EPOCH"] for r in placebo] == ["Screening", "Treatment"]
        assert [r["TAETORD"] for r in placebo] == [1, 2]
        assert placebo[1]["ELEMENT"] == "Placebo Infusion"
        assert all(len(r["ARMCD"]) <= 8 for r in ta)

    def test_te_rows(self, domains):
        te = {r["ELEMENT"]: r for r in domains["TE"]}
        assert len(te) == 3
        assert te["Screening"]["TESTRL"] == "Consent"
        assert te["Drug Infusion"]["TESTRL"] == ""

    def test_tv_rows_follow_encounter_chain(self, domains):
        tv = domains["TV"]
        assert [r["VISIT"] for r in tv] == ["Visit 1", "Visit 2"]
        assert [r["VISITNUM"] for r in tv] == [1, 2]

    def test_ti_rows(self, domains):
        ti = domains["TI"]
        assert len(ti) == 2
        by_cat = {r["IECAT"]: r for r in ti}
        assert by_cat["INCLUSION"]["IETESTCD"] == "INCL001"
        assert by_cat["INCLUSION"]["IETEST"] == "Age >= 18 years"
        assert by_cat["EXCLUSION"]["IETESTCD"] == "EXCL002"

    def test_write_domains_csv(self, domains, tmp_path):
        written = write_domains(domains, tmp_path)
        assert len(written) == 5
        with open(tmp_path / "TA.csv", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 4
        assert rows[0]["DOMAIN"] == "TA"


EXT = "https://example.org/usdm/ext/sdtm/"


def _ext_attr(name: str, value: str, n: int) -> dict:
    return {"id": f"ExtensionAttribute_{name}_{n}", "url": EXT + name,
            "valueString": value, "instanceType": "ExtensionAttribute"}


def _with_codes() -> dict:
    """The fixture with ARMCD/ETCD/VISITNUM stated as extension attributes."""
    usdm = _fixture()
    design = usdm["study"]["versions"][0]["studyDesigns"][0]
    for n, (arm, code) in enumerate(zip(design["arms"], ["Pbo", "Trt_Hi"])):
        arm["extensionAttributes"] = [_ext_attr("ARMCD", code, n)]
    for n, (el, code) in enumerate(zip(design["elements"], ["SCRN", "PBO", "DRUG"])):
        el["extensionAttributes"] = [_ext_attr("ETCD", code, n)]
    for n, (enc, num) in enumerate(zip(design["encounters"], ["3.5", "101.0"])):
        enc["extensionAttributes"] = [_ext_attr("VISITNUM", num, n)]
    return usdm


class TestStatedCodes:
    def test_armcd_from_extension(self):
        ta = generate_domains(_with_codes())["TA"]
        assert {r["ARM"]: r["ARMCD"] for r in ta} == {
            "Placebo": "Pbo", "Treatment": "Trt_Hi"}

    def test_etcd_from_extension_in_ta_and_te(self):
        domains = generate_domains(_with_codes())
        expected = {"Screening": "SCRN", "Placebo Infusion": "PBO",
                    "Drug Infusion": "DRUG"}
        assert {r["ELEMENT"]: r["ETCD"] for r in domains["TE"]} == expected
        assert {r["ELEMENT"]: r["ETCD"] for r in domains["TA"]} == expected

    def test_visitnum_from_extension(self):
        tv = generate_domains(_with_codes())["TV"]
        assert [r["VISITNUM"] for r in tv] == [3.5, 101]
        assert isinstance(tv[1]["VISITNUM"], int)  # "101.0" written as 101

    def test_url_matched_on_last_segment_only(self):
        usdm = _fixture()
        arm = usdm["study"]["versions"][0]["studyDesigns"][0]["arms"][0]
        arm["extensionAttributes"] = [
            {"id": "X1", "url": "https://example.org/NOTARMCD", "valueString": "BAD",
             "instanceType": "ExtensionAttribute"},
            {"id": "X2", "url": "https://other.example/ns/armcd/", "valueString": "Pbo",
             "instanceType": "ExtensionAttribute"},
        ]
        ta = generate_domains(usdm)["TA"]
        assert {r["ARMCD"] for r in ta if r["ARM"] == "Placebo"} == {"Pbo"}

    def test_without_extensions_derivation_is_unchanged(self, domains):
        assert {r["ARM"]: r["ARMCD"] for r in domains["TA"]} == {
            "Placebo": "PLACEBO", "Treatment": "TREATMEN"}
        assert [r["ETCD"] for r in domains["TE"]] == ["SCREENIN", "PLACEBOI", "DRUGINFU"]

    def test_derived_code_avoids_stated_code(self):
        usdm = _fixture()
        arms = usdm["study"]["versions"][0]["studyDesigns"][0]["arms"]
        # Arm 2 states the code that arm 1's name would derive to.
        arms[1]["extensionAttributes"] = [_ext_attr("ARMCD", "PLACEBO", 0)]
        ta = generate_domains(usdm)["TA"]
        codes = {r["ARM"]: r["ARMCD"] for r in ta}
        assert codes["Treatment"] == "PLACEBO"
        assert codes["Placebo"] != "PLACEBO"

    def test_invalid_visitnum_falls_back_to_sequence(self):
        usdm = _fixture()
        enc = usdm["study"]["versions"][0]["studyDesigns"][0]["encounters"]
        enc[0]["extensionAttributes"] = [_ext_attr("VISITNUM", "Day 1", 0)]
        enc[1]["extensionAttributes"] = [_ext_attr("VISITNUM", "nan", 1)]
        tv = generate_domains(usdm)["TV"]
        assert [r["VISITNUM"] for r in tv] == [1, 2]


class TestRealExamples:
    """Smoke tests against the downloaded USDM v4.0.0 example files."""

    @pytest.mark.parametrize("name,arms,visits", [
        ("arms_epochs", 2, 3),
        ("simple_1", 2, 5),
        ("eligibility_criteria_1", 2, 5),
    ])
    def test_example_row_counts(self, name, arms, visits):
        path = EXAMPLES_DIR / f"{name}.json"
        if not path.exists():
            pytest.skip(f"example file {path} not downloaded")
        usdm = json.loads(path.read_text(encoding="utf-8"))
        domains = generate_domains(usdm)
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
        assert len(domains["TA"]) == sum(
            len(c["elementIds"]) for c in design["studyCells"])
        assert len({r["ARMCD"] for r in domains["TA"]}) == arms
        assert len(domains["TE"]) == len(design["elements"])
        assert len(domains["TV"]) == visits
        assert len(domains["TI"]) == len(design["eligibilityCriteria"])
        assert domains["TS"]  # never empty


class TestSources:
    """generate_domains_with_sources: USDM ids per generated row."""

    @pytest.fixture()
    def result(self):
        return generate_domains_with_sources(_fixture())

    def test_domains_unchanged(self, result):
        domains, _ = result
        assert domains == generate_domains(_fixture())

    def test_sources_parallel_to_rows(self, result):
        domains, sources = result
        assert set(sources) == set(domains)
        for d in domains:
            assert len(sources[d]) == len(domains[d])

    def test_ta_ids(self, result):
        domains, sources = result
        by_row = {(r["ARM"], r["EPOCH"]): s["usdm_ids"]
                  for r, s in zip(domains["TA"], sources["TA"])}
        assert by_row[("Placebo", "Treatment")] == [
            "StudyArm_1", "StudyEpoch_2", "StudyCell_2", "StudyElement_2"]
        assert by_row[("Treatment", "Screening")] == [
            "StudyArm_2", "StudyEpoch_1", "StudyCell_3", "StudyElement_1"]

    def test_te_tv_ti_ids(self, result):
        _, sources = result
        assert [s["usdm_ids"] for s in sources["TE"]] == [
            ["StudyElement_1"], ["StudyElement_2"], ["StudyElement_3"]]
        assert [s["usdm_ids"] for s in sources["TV"]] == [
            ["Encounter_1"], ["Encounter_2"]]
        assert [s["usdm_ids"] for s in sources["TI"]] == [
            ["EligibilityCriterion_1", "EligibilityCriterionItem_1"],
            ["EligibilityCriterion_2", "EligibilityCriterionItem_2"]]

    def test_ts_ids_and_attributes(self, result):
        domains, sources = result
        ts = {r["TSPARMCD"]: (s["usdm_ids"], s["usdm_attribute"])
              for r, s in zip(domains["TS"], sources["TS"])}
        assert ts == {
            "TITLE": (["StudyTitle_1"], "StudyTitle_1.text"),
            "SPONSOR": (["Organization_2"], "Organization_2.name"),
            "REGID": (["StudyIdentifier_1"], "StudyIdentifier_1.text"),
            "TPHASE": (["AliasCode_C21"], "InterventionalStudyDesign_1.studyPhase"),
            "INTMODEL": (["Code_C22"], "InterventionalStudyDesign_1.model"),
            "TBLIND": (["AliasCode_C23"], "InterventionalStudyDesign_1.blindingSchema"),
            "STYPE": (["Code_C20"], "InterventionalStudyDesign_1.studyType"),
            "PLANSUB": (["Quantity_1"],
                        "StudyDesignPopulation_1.plannedEnrollmentNumber"),
        }

    def test_duplicate_names_keep_exact_ids(self):
        # Two elements with the same name: a join by name would have to guess;
        # the ids are recorded while building, so each row keeps its own.
        usdm = _fixture()
        elements = usdm["study"]["versions"][0]["studyDesigns"][0]["elements"]
        elements[2]["name"] = elements[1]["name"]
        domains, sources = generate_domains_with_sources(usdm)
        assert [r["ELEMENT"] for r in domains["TE"]][1:] == ["Placebo Infusion"] * 2
        assert [s["usdm_ids"] for s in sources["TE"]][1:] == [
            ["StudyElement_2"], ["StudyElement_3"]]
        ta_elements = [s["usdm_ids"][3] for s in sources["TA"]]
        assert ta_elements == ["StudyElement_1", "StudyElement_2",
                               "StudyElement_1", "StudyElement_3"]

    def test_duplicate_ids_give_empty_list(self):
        # Two criteria carry the same id, and the planned-enrolment Quantity
        # reuses an element's id: such an id names no single instance, so the
        # rows read from them get [] rather than a guess.
        usdm = _fixture()
        design = usdm["study"]["versions"][0]["studyDesigns"][0]
        design["eligibilityCriteria"][1]["id"] = "EligibilityCriterion_1"
        design["population"]["plannedEnrollmentNumber"]["id"] = "StudyElement_3"
        domains, sources = generate_domains_with_sources(usdm)
        assert len(domains["TI"]) == 2
        assert [s["usdm_ids"] for s in sources["TI"]] == [[], []]
        plansub = [s for r, s in zip(domains["TS"], sources["TS"])
                   if r["TSPARMCD"] == "PLANSUB"]
        assert plansub == [{"usdm_ids": [], "usdm_attribute": None}]
        assert [s["usdm_ids"] for s in sources["TE"]] == [
            ["StudyElement_1"], ["StudyElement_2"], []]
        assert [s["usdm_ids"] != [] for s in sources["TA"]] == [True, True, True, False]
        assert all(s["usdm_ids"] for s in sources["TV"])  # others unaffected

    def test_missing_id_gives_empty_list(self):
        usdm = _fixture()
        del usdm["study"]["versions"][0]["studyDesigns"][0]["elements"][0]["id"]
        _, sources = generate_domains_with_sources(usdm)
        assert sources["TE"][0]["usdm_ids"] == []
        assert sources["TE"][1]["usdm_ids"] == ["StudyElement_2"]

    def test_example_files_have_ids_for_every_row(self):
        for path in sorted(EXAMPLES_DIR.glob("*.json")):
            usdm = json.loads(path.read_text(encoding="utf-8"))
            if "study" not in usdm:
                continue
            _, sources = generate_domains_with_sources(usdm)
            for d, srcs in sources.items():
                assert all(s["usdm_ids"] for s in srcs), (path.name, d)
