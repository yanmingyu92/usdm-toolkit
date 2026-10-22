"""Tests for the rules module (YAML-defined conformance rules on USDM JSON)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from usdm_toolkit.rules import load_rules, run_rules

EXAMPLES_DIR = Path(__file__).parent.parent / "data" / "examples"


def _usdm(**design_kwargs) -> dict:
    design = {
        "id": "InterventionalStudyDesign_1", "name": "D1", "rationale": "r",
        "model": {"id": "Code_1", "decode": "Parallel Study",
                  "instanceType": "Code"},
        "population": {"id": "StudyDesignPopulation_1", "name": "POP",
                       "includesHealthySubjects": False,
                       "instanceType": "StudyDesignPopulation"},
        "instanceType": "InterventionalStudyDesign",
    }
    design.update(design_kwargs)
    return {
        "study": {
            "id": "Study_1", "name": "S", "instanceType": "Study",
            "versions": [{
                "id": "StudyVersion_1", "versionIdentifier": "1",
                "rationale": "r", "instanceType": "StudyVersion",
                "studyIdentifiers": [{"id": "SI_1", "text": "X", "scopeId": "O1",
                                      "instanceType": "StudyIdentifier"}],
                "titles": [{"id": "ST_1", "text": "T",
                            "instanceType": "StudyTitle"}],
                "studyDesigns": [design],
            }],
        },
    }


@pytest.fixture()
def rules():
    return load_rules()  # bundled library


class TestLibrary:
    def test_library_loads_five_rules(self, rules):
        assert len(rules) == 5
        assert {r.id for r in rules} == {
            "USDM-REQ-001", "USDM-REQ-002", "USDM-REQ-003",
            "USDM-REQ-004", "USDM-REQ-005",
        }
        assert all(r.severity == "error" for r in rules)

    def test_clean_instance_has_no_violations(self, rules):
        violations = run_rules(_usdm(), rules)
        assert violations == []

    def test_missing_identifiers_flagged(self, rules):
        usdm = _usdm()
        usdm["study"]["versions"][0]["studyIdentifiers"] = []
        violations = run_rules(usdm, rules)
        assert [v.rule_id for v in violations] == ["USDM-REQ-001"]
        assert violations[0].node_id == "StudyVersion_1"

    def test_missing_titles_flagged(self, rules):
        usdm = _usdm()
        del usdm["study"]["versions"][0]["titles"]
        violations = run_rules(usdm, rules)
        assert [v.rule_id for v in violations] == ["USDM-REQ-002"]

    def test_arm_without_type_flagged(self, rules):
        usdm = _usdm(arms=[{"id": "StudyArm_1", "name": "A",
                            "instanceType": "StudyArm"}])
        violations = run_rules(usdm, rules)
        assert [v.rule_id for v in violations] == ["USDM-REQ-003"]
        assert violations[0].node_id == "StudyArm_1"

    def test_encounter_with_empty_name_flagged(self, rules):
        usdm = _usdm(encounters=[
            {"id": "Encounter_1", "name": "", "type": {},
             "instanceType": "Encounter"},
            {"id": "Encounter_2", "name": "V2", "type": {},
             "instanceType": "Encounter"},
        ])
        violations = run_rules(usdm, rules)
        assert [v.rule_id for v in violations] == ["USDM-REQ-004"]
        assert violations[0].node_id == "Encounter_1"

    def test_design_without_model_flagged(self, rules):
        usdm = _usdm()
        del usdm["study"]["versions"][0]["studyDesigns"][0]["model"]
        violations = run_rules(usdm, rules)
        assert [v.rule_id for v in violations] == ["USDM-REQ-005"]

    def test_custom_rules_dir(self, tmp_path):
        (tmp_path / "custom.yml").write_text(
            "rules:\n"
            "  - id: CUSTOM-001\n"
            "    description: Study must have a name\n"
            "    severity: warning\n"
            "    scope: Study\n"
            "    expression: $exists(name) and $length(name) > 0\n",
            encoding="utf-8",
        )
        rules = load_rules(tmp_path)
        assert len(rules) == 1 and rules[0].severity == "warning"
        assert run_rules(_usdm(), rules) == []


class TestRealExamples:
    @pytest.mark.parametrize("name", ["arms_epochs", "simple_1",
                                      "eligibility_criteria_1"])
    def test_examples_pass_library(self, rules, name):
        path = EXAMPLES_DIR / f"{name}.json"
        if not path.exists():
            pytest.skip(f"example file {path} not downloaded")
        usdm = json.loads(path.read_text(encoding="utf-8"))
        violations = run_rules(usdm, rules)
        assert violations == []
