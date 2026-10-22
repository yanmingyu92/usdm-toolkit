"""Tests for ct_align core logic, using small synthetic fixtures.

The fixtures model the inconsistency patterns reported in cdisc-org/DDF-RA
issues #716 (abstract-class attributes carrying a subclass's C-code),
#717 (classification definition without a value list) and #718 (classes in
the YAML that are absent from the CT workbook).
"""

from __future__ import annotations

import openpyxl
import pytest
import yaml

from usdm_toolkit.ct_align.checker import check, load_ct, load_yaml_model
from usdm_toolkit.ct_align.report import render_markdown

CT_HEADER = [
    "Row #", "Entity Name", "Role", "Inherited From", "Logical Data Model Name",
    "NCI C-code", "CT Item Preferred Name", "Synonym(s)", "Definition",
    "Has Value List", "Codelist URL",
]

# (row#, entity, role, inherited, name, ccode, term, synonym, definition, hasVL, url)
CT_ROWS = [
    (1, "SyntaxTemplate", "Entity", None, "SyntaxTemplate", "C100001",
     "Syntax Template", None, "A template.", "N/A", None),
    (2, "SyntaxTemplate", "Attribute", None, "text", "C100002",
     "Syntax Template Text", None, "A structured text string.", "N", None),
    (3, "Characteristic", "Entity", "SyntaxTemplate", "Characteristic", "C100003",
     "Characteristic", None, "A characteristic.", "N/A", None),
    (4, "Characteristic", "Attribute", "SyntaxTemplate", "text", "C100004",
     "Characteristic Text", None, "An instance of structured text.", "N", None),
    (5, "Procedure", "Entity", None, "Procedure", "C100005",
     "Procedure", None, "A procedure.", "N/A", None),
    (6, "Procedure", "Attribute", None, "procedureType", "C100006",
     "Procedure Type", None,
     "A characterization or classification of the study procedure.", "N", None),
    (7, "Endpoint", "Entity", None, "Endpoint", "C100007",
     "Endpoint", None, "An endpoint.", "N/A", None),
    (8, "Endpoint", "Complex Datatype Relationship", None, "level", "C100008",
     "Study Endpoint Level", None,
     "A characterization or classification of the study endpoint.", "Y (C100009)",
     None),
    (9, "Study", "Entity", None, "Study", "C100010", "Clinical Study", None,
     "A clinical study.", "N/A", None),
    (10, "Study", "Attribute", None, "name", "C100011", "Clinical Study Name",
     None, "The literal identifier.", "N", None),
]

YAML_MODEL = {
    # #716 pattern: abstract class attribute carries the subclass's C-code.
    "SyntaxTemplate": {
        "NCI C-Code": "C100001",
        "Preferred Term": "Syntax Template",
        "Definition": "A template.",
        "Attributes": {
            "text": {
                "Type": [{"$ref": "#/string"}],
                "NCI C-Code": "C100004",  # CT row 4: Characteristic.text
                "Preferred Term": "Characteristic Text",
                "Definition": "An instance of structured text.",
            },
        },
    },
    "Characteristic": {
        "NCI C-Code": "C100003",
        "Preferred Term": "Characteristic",
        "Definition": "A characteristic.",
        "Attributes": {
            "text": {
                "Type": [{"$ref": "#/string"}],
                "NCI C-Code": "C100004",
                "Preferred Term": "Characteristic Text",
                "Definition": "An instance of structured text.",
            },
        },
    },
    # #717 pattern: consistent between the files, but no value list.
    "Procedure": {
        "NCI C-Code": "C100005",
        "Preferred Term": "Procedure",
        "Definition": "A procedure.",
        "Attributes": {
            "procedureType": {
                "Type": [{"$ref": "#/string"}],
                "NCI C-Code": "C100006",
                "Preferred Term": "Procedure Type",
                "Definition": "A characterization or classification of the study procedure.",
            },
        },
    },
    # Value-list attribute correctly typed as Code.
    "Endpoint": {
        "NCI C-Code": "C100007",
        "Preferred Term": "Endpoint",
        "Definition": "An endpoint.",
        "Attributes": {
            "level": {
                "Type": [{"$ref": "#/Code"}],
                "NCI C-Code": "C100008",
                "Preferred Term": "Study Endpoint Level",
                "Definition": "A characterization or classification of the study endpoint.",
            },
        },
    },
    # #718 pattern: class absent from the CT workbook.
    "ExtensionAttribute": {
        "Attributes": {
            "url": {"Type": [{"$ref": "#/string"}]},
        },
    },
    # Class-level term mismatch + attribute missing a CT row + unknown C-code.
    "Study": {
        "NCI C-Code": "C100010",
        "Preferred Term": "Study (wrong term)",
        "Definition": "A clinical study.",
        "Attributes": {
            "name": {
                "Type": [{"$ref": "#/string"}],
                "NCI C-Code": "C999999",  # not present in CT at all
                "Preferred Term": "Clinical Study Name",
                "Definition": "The literal identifier.",
            },
            "ghost": {
                "Type": [{"$ref": "#/string"}],
                "NCI C-Code": "C100011",
                "Preferred Term": "Clinical Study Name",
                "Definition": "The literal identifier.",
            },
        },
    },
}


@pytest.fixture()
def yaml_path(tmp_path):
    path = tmp_path / "dataStructure.yml"
    path.write_text(yaml.safe_dump(YAML_MODEL, sort_keys=False), encoding="utf-8")
    return str(path)


@pytest.fixture()
def ct_path(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "DDF Entities&Attributes"
    ws.append(CT_HEADER)
    for row in CT_ROWS:
        ws.append(list(row))
    wb.create_sheet("DDF valid value sets")
    path = tmp_path / "USDM_CT.xlsx"
    wb.save(path)
    return str(path)


@pytest.fixture()
def findings(yaml_path, ct_path):
    model = load_yaml_model(yaml_path)
    ct = load_ct(ct_path)
    return check(model, ct)


def rules(findings):
    return [f.rule for f in findings]


def test_ct_parsing(ct_path):
    ct = load_ct(ct_path)
    assert set(ct.entities) == {"SyntaxTemplate", "Characteristic", "Procedure",
                                "Endpoint", "Study"}
    assert ("SyntaxTemplate", "text") in ct.attributes
    assert ct.code_owners("C100004") == ["Characteristic.text"]


def test_abstract_class_attr_carries_subclass_ccode(findings):
    """Issue #716 signature: mismatch + YAML code owned by another CT row."""
    mismatches = [f for f in findings
                  if f.rule == "ATTR_CCODE_MISMATCH" and f.location == "SyntaxTemplate.text"]
    assert len(mismatches) == 1
    f = mismatches[0]
    assert f.ccode_yaml == "C100004"
    assert f.ccode_ct == "C100002"
    assert "Characteristic.text" in f.message
    # term and definition mismatches accompany the C-code mismatch
    assert "ATTR_TERM_MISMATCH" in rules(findings)
    assert "ATTR_DEFINITION_MISMATCH" in rules(findings)
    # the concrete subclass itself is consistent
    assert not [f for f in findings
                if f.rule == "ATTR_CCODE_MISMATCH" and f.location == "Characteristic.text"]


def test_classification_without_value_list(findings):
    """Issue #717 pattern."""
    flagged = [f for f in findings if f.rule == "CLASSIFICATION_WITHOUT_VALUE_LIST"]
    assert [f.location for f in flagged] == ["Procedure.procedureType"]


def test_class_not_in_ct(findings):
    """Issue #718 pattern."""
    flagged = [f for f in findings if f.rule == "CLASS_NOT_IN_CT"]
    assert [f.location for f in flagged] == ["ExtensionAttribute"]


def test_ccode_not_in_ct(findings):
    flagged = [f for f in findings if f.rule == "CCODE_NOT_IN_CT"]
    assert [(f.location, f.ccode_yaml) for f in flagged] == [("Study.name", "C999999")]


def test_attr_not_in_ct(findings):
    flagged = [f for f in findings if f.rule == "ATTR_NOT_IN_CT"]
    assert [f.location for f in flagged] == ["Study.ghost"]


def test_class_term_mismatch(findings):
    flagged = [f for f in findings if f.rule == "CLASS_TERM_MISMATCH"]
    assert [f.location for f in flagged] == ["Study"]


def test_ct_attr_not_in_yaml(findings):
    # Study.name exists in YAML but with a foreign C-code is irrelevant here;
    # no CT row should be reported missing except none — all CT attribute rows
    # have YAML counterparts carrying a C-code, except Study.name's ghost shift:
    # (Study, name) exists in YAML with C-code, so no coverage finding.
    flagged = [f for f in findings if f.rule == "CT_ATTR_NOT_IN_YAML"]
    assert flagged == []


def test_value_list_type_ok(findings):
    """Endpoint.level has a value list and is Code-typed: no finding."""
    flagged = [f for f in findings if f.rule == "VALUE_LIST_TYPE_MISMATCH"]
    assert flagged == []


def test_value_list_type_mismatch_detected(ct_path, tmp_path):
    model = {
        "Endpoint": {
            "NCI C-Code": "C100007",
            "Attributes": {
                "level": {
                    "Type": [{"$ref": "#/string"}],  # wrong: CT declares a value list
                    "NCI C-Code": "C100008",
                },
            },
        },
    }
    ct = load_ct(ct_path)
    findings = check(model, ct)
    flagged = [f for f in findings if f.rule == "VALUE_LIST_TYPE_MISMATCH"]
    assert [f.location for f in flagged] == ["Endpoint.level"]


def test_report_renders(findings):
    md = render_markdown(findings, yaml_source="a.yml", ct_source="b.xlsx")
    assert "# ct-align consistency report" in md
    assert "ATTR_CCODE_MISMATCH" in md
    assert "SyntaxTemplate.text" in md
