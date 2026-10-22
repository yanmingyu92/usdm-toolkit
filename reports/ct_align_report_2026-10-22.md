# ct-align report: dataStructure.yml vs USDM_CT.xlsx (USDM v4.0.0)

- Report date: 2026-10-22
- Tool: `usdm-toolkit` `ct-align` v0.1.0 (this repository)
- Model file: `data/source/dataStructure.yml` — cdisc-org/DDF-RA, tag `v4.0.0`, path `Deliverables/UML/dataStructure.yml`
- CT file: `data/source/USDM_CT.xlsx` — cdisc-org/DDF-RA, tag `v4.0.0`, path `Deliverables/CT/USDM_CT.xlsx`
- Both files exist under the `v4.0.0` tag; no fallback to `main` was needed. Provenance: `data/source/SOURCE.md`.

> Independent community tool; not a CDISC deliverable. See the disclaimer in `README.md`.

## 1. Method

`ct-align` parses every class and attribute in `dataStructure.yml` (top-level mapping;
attributes under `Attributes:`) and every row of the "DDF Entities&Attributes" sheet of
`USDM_CT.xlsx`, keyed by `(Entity Name, Logical Data Model Name)`. It then applies the
rules listed in the README: C-code / preferred term / definition equality per class and
attribute, resolution of which CT row actually owns a mismatched YAML C-code,
classes absent from CT, value-list vs YAML type consistency, a deterministic heuristic for
classification-style definitions without a value list, and reverse coverage of CT rows in
the YAML. No finding is hand-written; every table below is produced by the checker.

## 2. Summary of findings

| Rule | Severity | Count |
| --- | --- | --- |
| `ATTR_CCODE_MISMATCH` | error | 27 |
| `ATTR_TERM_MISMATCH` | error | 27 |
| `ATTR_DEFINITION_MISMATCH` | error | 27 |
| `CLASSIFICATION_WITHOUT_VALUE_LIST` | warning | 1 |
| `CLASS_NOT_IN_CT` | warning | 2 |
| `VALUE_LIST_TYPE_MISMATCH` | warning | 7 |
| `CT_ATTR_NOT_IN_YAML` | info | 172 |
| **Total** | | **263** |

No class-level mismatches, no `ATTR_NOT_IN_CT` and no `CCODE_NOT_IN_CT` findings: every
C-code referenced by the YAML exists somewhere in the CT workbook, and all 84 CT entities
appear in the YAML.

## 3. Cross-check against DDF-RA issues #716, #717, #718

### Issue #716 — abstract-class attributes carry a subclass's C-code (27 attributes)

**Reproduced: 27/27, with zero additional C-code mismatches.** Each of the 27
attributes differs on all three fields (C-code, preferred term, definition), and in every
case the YAML's C-code resolves to the CT row of the concrete subclass named in the issue.

| Attribute | YAML C-code | CT C-code | YAML code is the CT row of | Tool result |
| --- | --- | --- | --- | --- |
| `Identifier.text` | C215581 | C215450 (CT row 470) | `AdministrableProductIdentifier.text` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.description` | C207542 | C207517 (CT row 400) | `StudyCohort.description` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.includesHealthySubjects` | C207480 | C207518 (CT row 404) | `StudyCohort.includesHealthySubjects` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.label` | C207543 | C207519 (CT row 401) | `StudyCohort.label` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.name` | C207544 | C207520 (CT row 399) | `StudyCohort.name` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.notes` | C215547 | C215551 (CT row 408) | `StudyCohort.notes` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.plannedAge` | C207545 | C207701 (CT row 403) | `StudyCohort.plannedAge` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.plannedCompletionNumber` | C207546 | C207521 (CT row 405) | `StudyCohort.plannedCompletionNumber` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.plannedEnrollmentNumber` | C207702 | C207522 (CT row 406) | `StudyCohort.plannedEnrollmentNumber` | Reproduced (code, term and definition all differ) |
| `PopulationDefinition.plannedSex` | C207541 | C207523 (CT row 402) | `StudyCohort.plannedSex` | Reproduced (code, term and definition all differ) |
| `ScheduledInstance.description` | C207531 | C207453 (CT row 244) | `ScheduledActivityInstance.description` | Reproduced (code, term and definition all differ) |
| `ScheduledInstance.label` | C207532 | C207454 (CT row 245) | `ScheduledActivityInstance.label` | Reproduced (code, term and definition all differ) |
| `ScheduledInstance.name` | C207533 | C207455 (CT row 243) | `ScheduledActivityInstance.name` | Reproduced (code, term and definition all differ) |
| `StudyDesign.characteristics` | C215632 | C207547 (CT row 40) | `InterventionalStudyDesign.characteristics` | Reproduced (code, term and definition all differ) |
| `StudyDesign.description` | C215627 | C147139 (CT row 37) | `InterventionalStudyDesign.description` | Reproduced (code, term and definition all differ) |
| `StudyDesign.label` | C215628 | C207548 (CT row 39) | `InterventionalStudyDesign.label` | Reproduced (code, term and definition all differ) |
| `StudyDesign.name` | C215626 | C201338 (CT row 36) | `InterventionalStudyDesign.name` | Reproduced (code, term and definition all differ) |
| `StudyDesign.notes` | C215634 | C215508 (CT row 34) | `InterventionalStudyDesign.notes` | Reproduced (code, term and definition all differ) |
| `StudyDesign.rationale` | C215629 | C142705 (CT row 38) | `InterventionalStudyDesign.rationale` | Reproduced (code, term and definition all differ) |
| `StudyDesign.studyPhase` | C215630 | C48281 (CT row 42) | `InterventionalStudyDesign.studyPhase` | Reproduced (code, term and definition all differ) |
| `StudyDesign.studyType` | C215631 | C142175 (CT row 41) | `InterventionalStudyDesign.studyType` | Reproduced (code, term and definition all differ) |
| `StudyDesign.therapeuticAreas` | C215633 | C101302 (CT row 35) | `InterventionalStudyDesign.therapeuticAreas` | Reproduced (code, term and definition all differ) |
| `SyntaxTemplate.description` | C207475 | C207575 (CT row 286) | `Characteristic.description` | Reproduced (code, term and definition all differ) |
| `SyntaxTemplate.label` | C207476 | C207576 (CT row 287) | `Characteristic.label` | Reproduced (code, term and definition all differ) |
| `SyntaxTemplate.name` | C207477 | C207577 (CT row 284) | `Characteristic.name` | Reproduced (code, term and definition all differ) |
| `SyntaxTemplate.notes` | C215548 | C215536 (CT row 289) | `Characteristic.notes` | Reproduced (code, term and definition all differ) |
| `SyntaxTemplate.text` | C207478 | C207578 (CT row 285) | `Characteristic.text` | Reproduced (code, term and definition all differ) |

### Issue #717 — `Procedure.procedureType`: a classification without a value list

**Reproduced.** The `CLASSIFICATION_WITHOUT_VALUE_LIST` rule flags exactly one CT row:
`Procedure.procedureType` (CT row 141, C188848), definition "A characterization or
classification of the study procedure.", Has Value List = N. The contrasting example from
the issue, `Endpoint.level` (CT row 73), declares `Y (C188726)` and is not flagged. Note
that the two files are mutually consistent here (both treat `procedureType` as an uncoded
string); the rule detects the CT-side design question the issue raises.

### Issue #718 — `ExtensionAttribute` and `ExtensionClass` still in dataStructure.yml

**Reproduced.** `CLASS_NOT_IN_CT` flags exactly the two classes named in the issue:
`ExtensionAttribute` (13 attributes) and `ExtensionClass` (4 attributes),
both present in `dataStructure.yml` v4.0.0, neither carrying an NCI C-code, preferred term
or definition, and neither having an entity row in `USDM_CT.xlsx`.

## 4. Findings beyond the three issues

### 4.1 `VALUE_LIST_TYPE_MISMATCH` (7)

YAML attributes typed as `Code`/`AliasCode` whose CT row declares `Has Value List = N`.
Candidates for review — they may be intentional (a `Code` structure without a bound
codelist) or missing value-list bindings:

| Location | YAML type | CT Has Value List |
| --- | --- | --- |
| `AliasCode.standardCode` | #/Code | N |
| `AliasCode.standardCodeAliases` | #/Code | N |
| `BiomedicalConcept.code` | #/AliasCode | N |
| `BiomedicalConceptCategory.code` | #/AliasCode | N |
| `BiomedicalConceptProperty.code` | #/AliasCode | N |
| `CommentAnnotation.codes` | #/Code | N |
| `ResponseCode.code` | #/Code | N |

### 4.2 `CT_ATTR_NOT_IN_YAML` (172, informational)

All 172 findings are CT rows with Role = "Relationship". Two systematic patterns:

- **83** relationship attributes exist only in CT; in the YAML they are
  serialized as `*Id` / `*Ids` string references instead (e.g. CT `Activity.next` vs YAML
  `Activity.nextId`). This matches the API-oriented design of `dataStructure.yml`.
- **89** relationship attributes do exist in the YAML as object references but
  carry no C-code, preferred term or definition, although CT assigns them one (e.g.
  `Activity.definedProcedures`). Consumers of the YAML therefore lose the terminology
  metadata for relationships.

## 5. Reproduce

```bash
pip install -e .[dev]
python -m usdm_toolkit.cli ct-align \
    --yaml data/source/dataStructure.yml \
    --ct data/source/USDM_CT.xlsx \
    --out reports/ct_align_raw_2026-10-22.md
pytest
```

The raw, complete checker output (all findings, all tables) is in
`reports/ct_align_raw_2026-10-22.md`. Test suite: 11 tests, all passing (synthetic fixtures
covering each rule).
