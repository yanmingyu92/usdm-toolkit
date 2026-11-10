"""Tests for trace_check: cross-artifact consistency between USDM and SDTM."""

from __future__ import annotations

import json

import pytest
from _tc_fixtures import (consistent_sdtm, consistent_usdm, deep, design,
                          mutate_rows, version)

from usdm_toolkit.trace_check import run_trace_check
from usdm_toolkit.trace_check.loaders import load_dataset, load_sdtm_dir
from usdm_toolkit.trace_check.matching import match_labels, normalize
from usdm_toolkit.trace_check.report import (render_json, render_markdown,
                                             write_xlsx)
from usdm_toolkit.trace_check.usdm_view import StudyView


def _ids(report, severities=("error", "warning")) -> set[str]:
    return {f.rule_id for f in report.findings if f.severity in severities}


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

class TestMatching:
    def test_normalize_collapses_case_and_punctuation(self):
        assert normalize("High - Start") == normalize("HIGH_START") == "high start"

    def test_exact_and_fuzzy_pairs(self):
        result = match_labels(["Screening", "Week 2"], ["SCREEN", "WEEK 2", "WEEK 4"])
        pairs = {(p.left, p.right): p.exact for p in result.pairs}
        assert pairs[("Week 2", "WEEK 2")] is True
        assert pairs[("Screening", "SCREEN")] is False   # fuzzy, not exact
        assert result.right_only == ("WEEK 4",)
        assert result.left_only == ()

    def test_aliases_are_used(self):
        result = match_labels([("E1", ("E1", "Screening 1"))], ["SCREENING 1"])
        assert result.pairs[0].left == "E1"
        assert result.pairs[0].exact

    def test_each_right_value_matches_at_most_once(self):
        result = match_labels(["Week 2", "Week 2 "], ["WEEK 2"])
        assert len(result.pairs) == 1
        assert len(result.left_only) == 1


class TestStudyView:
    def test_view_extracts_design(self):
        view = StudyView.from_usdm(consistent_usdm())
        assert [a.display for a in view.arms] == ["Placebo", "Drugamab 10 mg"]
        assert [e.display for e in view.encounters] == ["Screening", "Week 2"]
        assert view.arm_paths["StudyArm_1"] == ("Screen", "Placebo")
        assert view.registry_id == "NCT00000001"
        assert view.phase == "Phase II Trial"
        assert view.planned_enrollment == 60
        crit = {(c.category, c.number): c.text for c in view.criteria}
        assert crit[("INCLUSION", 1)] == "Age at least 18 years"   # tags stripped

    def test_soa_lists_planned_bc_by_encounter(self):
        view = StudyView.from_usdm(consistent_usdm())
        planned = {(p.encounter_id, p.bc_code) for p in view.soa}
        assert planned == {("Encounter_1", "C25298"), ("Encounter_1", "C25208"),
                           ("Encounter_2", "C25298")}

    def test_usdm_tags_and_refs_are_resolved(self):
        usdm = deep(consistent_usdm())
        v = version(usdm)
        v["dictionaries"] = [{"id": "Dict_1", "parameterMaps": [
            {"tag": "min_age", "reference":
             '<usdm:ref klass="Quantity" id="Quantity_9" attribute="value">'
             '</usdm:ref>'},
            {"tag": "pop", "reference":
             '<usdm:ref klass="StudyDesignPopulation" id="Pop_1" '
             'attribute="description"></usdm:ref>'}]}]
        design(usdm)["population"].update(
            {"id": "Pop_1", "description": "Probable <b>AD</b>",
             "plannedMinimumAge": {"id": "Quantity_9", "value": 50.0}})
        v["eligibilityCriterionItems"][0].update({
            "dictionaryId": "Dict_1",
            "text": '<p>At least <usdm:tag name="min_age"/> years; '
                    '<usdm:tag name="pop"/> diagnosis</p>'})
        view = StudyView.from_usdm(usdm)
        crit = {(c.category, c.number): c.text for c in view.criteria}
        assert crit[("INCLUSION", 1)] == "At least 50 years; Probable AD diagnosis"

    def test_unresolvable_tag_is_kept_visible(self):
        usdm = deep(consistent_usdm())
        version(usdm)["eligibilityCriterionItems"][0]["text"] = \
            'Score <usdm:tag name="nowhere"/> or more'
        view = StudyView.from_usdm(usdm)
        assert "[nowhere]" in view.criteria[0].text

    def test_missing_design_does_not_crash(self):
        view = StudyView.from_usdm({"study": {"versions": [{}]}})
        assert view.arms == () and view.soa == ()


class TestLoaders:
    def test_dataset_json_v11(self, tmp_path):
        p = tmp_path / "dm.json"
        p.write_text(json.dumps({
            "datasetJSONVersion": "1.1.0", "name": "DM",
            "columns": [{"name": "USUBJID"}, {"name": "ARM"}],
            "rows": [["S1", "Placebo"]]}), encoding="utf-8")
        name, rows = load_dataset(p)
        assert name == "DM"
        assert rows == ({"USUBJID": "S1", "ARM": "Placebo"},)

    def test_dataset_json_v10(self, tmp_path):
        p = tmp_path / "ta.json"
        p.write_text(json.dumps({"clinicalData": {"itemGroupData": {"IG.TA": {
            "name": "TA",
            "items": [{"name": "ITEMGROUPDATASEQ"}, {"name": "ARM"}],
            "itemData": [[1, "Placebo"]]}}}}), encoding="utf-8")
        name, rows = load_dataset(p)
        assert name == "TA"
        assert rows == ({"ARM": "Placebo"},)

    def test_csv_and_dir(self, tmp_path):
        (tmp_path / "tv.csv").write_text("VISITNUM,VISIT\n1,SCREENING\n",
                                         encoding="utf-8")
        (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")
        data = load_sdtm_dir(tmp_path)
        assert set(data) == {"TV"}
        assert data["TV"][0]["VISIT"] == "SCREENING"

    def test_bad_json_raises_clear_error(self, tmp_path):
        p = tmp_path / "x.json"
        p.write_text("{not json", encoding="utf-8")
        with pytest.raises(ValueError, match="x.json"):
            load_dataset(p)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class TestConsistentStudy:
    def test_no_errors_or_warnings(self):
        report = run_trace_check(consistent_usdm(), consistent_sdtm())
        problems = [f for f in report.findings if f.severity != "info"]
        assert problems == [], problems

    def test_rules_skipped_when_dataset_missing(self):
        sdtm = {k: v for k, v in consistent_sdtm().items() if k != "SV"}
        report = run_trace_check(consistent_usdm(), sdtm)
        assert "TC-SV-001" in {s.rule_id for s in report.skipped}


class TestTrialDesignRules:
    def test_arm_missing_from_ta(self):
        sdtm = mutate_rows(consistent_sdtm(), "TA",
                           lambda rows: [r for r in rows if r["ARMCD"] != "DRG10"])
        assert "TC-TA-001" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_extra_arm_in_ta(self):
        def add(rows):
            return rows + [{**rows[0], "ARMCD": "X", "ARM": "Rescue Arm"}]
        sdtm = mutate_rows(consistent_sdtm(), "TA", add)
        assert "TC-TA-002" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_element_sequence_differs(self):
        usdm = deep(consistent_usdm())
        d = design(usdm)
        d["elements"].append({"id": "StudyElement_4", "name": "EL4",
                              "label": "Follow up"})
        d["epochs"][-1]["nextId"] = "StudyEpoch_3"
        d["epochs"].append({"id": "StudyEpoch_3", "name": "EP3",
                            "label": "Follow-up", "previousId": "StudyEpoch_2",
                            "nextId": None})
        d["studyCells"].append({"armId": "StudyArm_1", "epochId": "StudyEpoch_3",
                                "elementIds": ["StudyElement_4"]})
        ids = _ids(run_trace_check(usdm, consistent_sdtm()))
        assert {"TC-TA-003", "TC-TA-004", "TC-TE-001"} <= ids

    def test_visit_missing_from_tv(self):
        sdtm = mutate_rows(consistent_sdtm(), "TV", lambda rows: rows[:1])
        assert "TC-TV-001" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_extra_visit_in_tv(self):
        sdtm = mutate_rows(consistent_sdtm(), "TV", lambda rows: rows + [
            {**rows[0], "VISITNUM": 99, "VISIT": "RETRIEVAL"}])
        assert "TC-TV-002" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_criterion_text_differs(self):
        def edit(rows):
            rows[0]["IETEST"] = "Body mass index below 30"
            return rows
        sdtm = mutate_rows(consistent_sdtm(), "TI", edit)
        assert "TC-TI-002" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_abbreviated_criterion_is_info_not_warning(self):
        usdm = deep(consistent_usdm())
        version(usdm)["eligibilityCriterionItems"][1]["text"] = (
            "Pregnant or breastfeeding, including women planning pregnancy "
            "within 6 months after the last dose or with a positive test")
        report = run_trace_check(usdm, consistent_sdtm())
        assert "TC-TI-002" not in _ids(report)
        notes = [f for f in report.findings if f.rule_id == "TC-TI-002"]
        assert notes and notes[0].severity == "info" and notes[0].count == 1

    def test_criterion_missing(self):
        sdtm = mutate_rows(consistent_sdtm(), "TI", lambda rows: rows[:1])
        assert "TC-TI-001" in _ids(run_trace_check(consistent_usdm(), sdtm))


class TestTrialSummaryRules:
    def test_phase_mismatch(self):
        def edit(rows):
            return [{**r, "TSVAL": "Phase III Trial"} if r["TSPARMCD"] == "TPHASE"
                    else r for r in rows]
        report = run_trace_check(consistent_usdm(),
                                 mutate_rows(consistent_sdtm(), "TS", edit))
        hits = [f for f in report.findings if f.rule_id == "TC-TS-001"]
        assert hits and "TPHASE" in hits[0].sdtm_ref

    def test_enrollment_mismatch(self):
        def edit(rows):
            return [{**r, "TSVAL": "300"} if r["TSPARMCD"] == "PLANSUB" else r
                    for r in rows]
        report = run_trace_check(consistent_usdm(),
                                 mutate_rows(consistent_sdtm(), "TS", edit))
        assert "TC-TS-001" in _ids(report)

    def test_primary_objective_not_in_ts(self):
        usdm = deep(consistent_usdm())
        design(usdm)["objectives"].append({
            "id": "OBJ_2", "name": "OBJ2", "text": "To assess safety and "
            "tolerability of long term dosing",
            "level": {"decode": "Study Primary Objective"}})
        assert "TC-TS-002" in _ids(run_trace_check(usdm, consistent_sdtm()))


class TestSubjectDataRules:
    def test_dm_arm_not_in_protocol(self):
        def edit(rows):
            rows[0]["ARM"] = "Drugamab 20 mg"
            return rows
        sdtm = mutate_rows(consistent_sdtm(), "DM", edit)
        assert "TC-DM-001" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_screen_failure_arm_is_allowed(self):
        sdtm = mutate_rows(consistent_sdtm(), "DM", lambda rows: rows + [
            {**rows[0], "USUBJID": "SF", "ARMCD": "SCRNFAIL",
             "ARM": "Screen Failure", "ACTARMCD": "SCRNFAIL",
             "ACTARM": "Screen Failure"}])
        assert "TC-DM-001" not in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_actual_arm_differs_is_reported_as_info(self):
        def edit(rows):
            rows[0]["ACTARMCD"], rows[0]["ACTARM"] = "DRG10", "Drugamab 10 mg"
            return rows
        report = run_trace_check(consistent_usdm(),
                                 mutate_rows(consistent_sdtm(), "DM", edit))
        hits = [f for f in report.findings if f.rule_id == "TC-DM-002"]
        assert hits and hits[0].severity == "info" and hits[0].count == 1

    def test_unplanned_visit_in_sv(self):
        sdtm = mutate_rows(consistent_sdtm(), "SV", lambda rows: rows + [
            {**rows[0], "VISITNUM": 3, "VISIT": "WEEK 4"},
            {**rows[0], "VISITNUM": 1.1, "VISIT": "UNSCHEDULED 1.1"}])
        report = run_trace_check(consistent_usdm(), sdtm)
        hits = [f for f in report.findings if f.rule_id == "TC-SV-001"]
        assert len(hits) == 1 and "WEEK 4" in hits[0].sdtm_ref

    def test_unknown_element_in_se(self):
        sdtm = mutate_rows(consistent_sdtm(), "SE", lambda rows: rows + [
            {**rows[0], "ETCD": "OLE", "ELEMENT": "Open Label Extension"}])
        assert "TC-SE-001" in _ids(run_trace_check(consistent_usdm(), sdtm))

    def test_ex_treatment_spelling(self):
        usdm = deep(consistent_usdm())
        version(usdm)["studyInterventions"][0]["label"] = "Drugamib"
        version(usdm)["studyInterventions"][0]["name"] = "DRUGAMIB"
        report = run_trace_check(usdm, consistent_sdtm())
        hits = [f for f in report.findings if f.rule_id == "TC-EX-001"]
        assert hits and hits[0].severity == "warning"


class TestSoaRules:
    def test_planned_test_without_data(self):
        sdtm = mutate_rows(consistent_sdtm(), "VS",
                           lambda rows: [r for r in rows if r["VSTESTCD"] != "WEIGHT"])
        report = run_trace_check(consistent_usdm(), sdtm)
        hits = [f for f in report.findings if f.rule_id == "TC-SOA-001"]
        assert hits and "WEIGHT" in hits[0].sdtm_ref

    def test_planned_visit_without_data(self):
        sdtm = mutate_rows(consistent_sdtm(), "VS", lambda rows: [
            r for r in rows if not (r["VSTESTCD"] == "SYSBP" and r["VISITNUM"] == 2)])
        report = run_trace_check(consistent_usdm(), sdtm)
        hits = [f for f in report.findings if f.rule_id == "TC-SOA-002"]
        assert hits and "WEEK 2" in hits[0].message.upper()

    def test_unmapped_bc_is_info(self):
        usdm = deep(consistent_usdm())
        version(usdm)["biomedicalConcepts"][1]["code"]["standardCode"]["code"] = "C999"
        report = run_trace_check(usdm, consistent_sdtm())
        hits = [f for f in report.findings if f.rule_id == "TC-SOA-000"]
        assert hits and hits[0].severity == "info"

    def test_custom_bc_map(self):
        usdm = deep(consistent_usdm())
        version(usdm)["biomedicalConcepts"][1]["code"]["standardCode"]["code"] = "C999"
        report = run_trace_check(usdm, consistent_sdtm(),
                                 bc_map={"C999": ("VS", "WEIGHT")})
        assert not [f for f in report.findings if f.rule_id == "TC-SOA-000"]


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

class TestReports:
    @pytest.fixture()
    def report(self):
        sdtm = mutate_rows(consistent_sdtm(), "TV", lambda rows: rows[:1])
        return run_trace_check(consistent_usdm(), sdtm)

    def test_markdown(self, report):
        md = render_markdown(report, usdm_source="u.json", sdtm_source="sdtm/")
        assert "TC-TV-001" in md and "# trace-check report" in md

    def test_json(self, report):
        data = json.loads(render_json(report))
        assert data["summary"]["warning"] >= 1
        assert any(f["rule_id"] == "TC-TV-001" for f in data["findings"])

    def test_xlsx_has_p21_style_sheets(self, report, tmp_path):
        import openpyxl
        path = tmp_path / "r.xlsx"
        write_xlsx(report, path)
        wb = openpyxl.load_workbook(path)
        assert wb.sheetnames == ["Summary", "Issues", "Rules"]
        header = [c.value for c in wb["Issues"][1]]
        assert header[:3] == ["Rule ID", "Severity", "Category"]


def test_cli_trace_check(tmp_path):
    from usdm_toolkit.cli import main
    usdm_path = tmp_path / "study.json"
    usdm_path.write_text(json.dumps(consistent_usdm()), encoding="utf-8")
    sdtm_dir = tmp_path / "sdtm"
    sdtm_dir.mkdir()
    for name, rows in consistent_sdtm().items():
        cols = sorted({k for r in rows for k in r})
        (sdtm_dir / f"{name.lower()}.json").write_text(json.dumps({
            "datasetJSONVersion": "1.1.0", "name": name,
            "columns": [{"name": c} for c in cols],
            "rows": [[r.get(c) for c in cols] for r in rows]}), encoding="utf-8")
    out = tmp_path / "report.xlsx"
    code = main(["trace-check", "--usdm", str(usdm_path), "--sdtm", str(sdtm_dir),
                 "--out", str(out)])
    assert code == 0
    assert out.exists()


# ---------------------------------------------------------------------------
# Regression tests from code review (2026-11-10)
# ---------------------------------------------------------------------------

class TestReviewRegressions:
    @pytest.mark.parametrize("a,b", [("Arm A", "Arm B"), ("Drug A", "Drug B"),
                                     ("Screening Day -1", "Screening Day 1"),
                                     ("Week 2", "Week 12")])
    def test_labels_that_must_not_match(self, a, b):
        from usdm_toolkit.trace_check.matching import similarity
        assert similarity(a, b) < 0.8

    def test_number_subset_still_matches(self):
        from usdm_toolkit.trace_check.matching import similarity
        assert similarity("Week 2", "Week 2 Day 1") >= 0.8

    def test_single_letter_arm_difference_is_an_error(self):
        usdm = deep(consistent_usdm())
        design(usdm)["arms"][1].update({"name": "Arm A", "label": "Arm A"})
        def edit(rows):
            return [{**r, "ARM": "Arm B", "ACTARM": "Arm B"}
                    if r["ARMCD"] == "DRG10" else r for r in rows]
        sdtm = mutate_rows(consistent_sdtm(), "DM", edit)
        assert "TC-DM-001" in _ids(run_trace_check(usdm, sdtm))

    def test_duplicate_labels_do_not_create_false_gaps(self):
        result = match_labels(["Day 1", "Day 1"], ["DAY 1"])
        assert result.left_only == () and result.right_only == ()

    def test_phase_combinations_are_not_compatible(self):
        from usdm_toolkit.trace_check.matching import phase_compatible
        assert not phase_compatible("Phase II Trial", "Phase I/II Trial")
        assert phase_compatible("Phase 2", "Phase II Trial")
        assert phase_compatible("PHASE IIA TRIAL", "Phase IIa Trial")

    def test_bad_values_do_not_crash(self):
        usdm = deep(consistent_usdm())
        design(usdm)["elements"] = None
        design(usdm)["arms"].append(None)
        sdtm = mutate_rows(consistent_sdtm(), "TA", lambda rows: [
            {**r, "TAETORD": " "} for r in rows])
        report = run_trace_check(usdm, sdtm)
        assert isinstance(report.findings, tuple)

    def test_crashing_rule_is_recorded_not_raised(self):
        from usdm_toolkit.trace_check.model import Rule, RuleSpec
        def boom(ctx):
            raise RuntimeError("kaput")
            yield  # pragma: no cover
        rule = Rule((RuleSpec("TC-X-001", "boom", "Test", "error"),), boom)
        report = run_trace_check(consistent_usdm(), consistent_sdtm(), rules=(rule,))
        assert report.skipped[0].rule_id == "TC-X-001"
        assert "kaput" in report.skipped[0].reason

    def test_non_dataset_json_is_skipped(self, tmp_path):
        from usdm_toolkit.trace_check.loaders import scan_sdtm_dir
        (tmp_path / "define.json").write_text('{"odm": 1}', encoding="utf-8")
        (tmp_path / "tv.csv").write_text("VISIT\nSCREENING\n", encoding="utf-8")
        data, problems = scan_sdtm_dir(tmp_path)
        assert set(data) == {"TV"} and "define.json" in problems[0]

    def test_blank_armcd_not_reported_as_arm_switch(self):
        def edit(rows):
            rows[0]["ARMCD"] = ""
            return rows
        report = run_trace_check(consistent_usdm(),
                                 mutate_rows(consistent_sdtm(), "DM", edit))
        assert "TC-DM-002" not in {f.rule_id for f in report.findings}

    def test_truncated_ts_title_is_accepted(self):
        usdm = deep(consistent_usdm())
        long_title = "A Synthetic Study of Drugamab " + "in adults " * 30
        version(usdm)["titles"][0]["text"] = long_title
        def edit(rows):
            return [{**r, "TSVAL": long_title[:200]} if r["TSPARMCD"] == "TITLE"
                    else r for r in rows]
        report = run_trace_check(usdm, mutate_rows(consistent_sdtm(), "TS", edit))
        assert "TC-TS-001" not in _ids(report)

    def test_unscheduled_encounter_needs_no_sv(self):
        usdm = deep(consistent_usdm())
        encs = design(usdm)["encounters"]
        encs[-1]["nextId"] = "Encounter_3"
        encs.append({"id": "Encounter_3", "name": "E3", "label": "Unscheduled",
                     "previousId": encs[-1]["id"], "nextId": None})
        assert "TC-SV-002" not in _ids(run_trace_check(usdm, consistent_sdtm()))

    def test_formula_like_text_is_escaped_in_xlsx(self, tmp_path):
        import openpyxl
        from usdm_toolkit.trace_check.model import Finding, TraceReport
        report = TraceReport((Finding("TC-X", "info", "C", "=HYPERLINK(1)",
                                      "+x", "@y"),), ())
        write_xlsx(report, tmp_path / "r.xlsx")
        row = [c.value for c in openpyxl.load_workbook(tmp_path / "r.xlsx")["Issues"][2]]
        assert row[3] == "'=HYPERLINK(1)" and row[4] == "'+x" and row[5] == "'@y"


def test_cli_returns_2_on_unreadable_usdm(tmp_path, capsys):
    from usdm_toolkit.cli import main
    bad = tmp_path / "study.json"
    bad.write_text("[1, 2]", encoding="utf-8")
    (tmp_path / "sdtm").mkdir()
    assert main(["trace-check", "--usdm", str(bad), "--sdtm",
                 str(tmp_path / "sdtm")]) == 2
    assert "not a USDM JSON object" in capsys.readouterr().err
