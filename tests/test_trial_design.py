"""Tests for the trial_design module (USDM JSON -> SDTM Trial Design CSVs)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from usdm_toolkit.trial_design import generate_domains, write_domains

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
        assert ts["PHASE"] == "Phase II Trial"          # AliasCode -> standardCode
        assert ts["INTMODEL"] == "Parallel Study"
        assert ts["BLIND"] == "Double Blind Study"
        assert ts["STYPE"] == "Interventional Study"
        assert ts["ENROLL"] == "60"
        seqs = [r["TSSEQ"] for r in domains["TS"]]
        assert seqs == list(range(1, len(seqs) + 1))

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
