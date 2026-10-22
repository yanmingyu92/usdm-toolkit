# USDM conformance rules report

- Report date: 2026-10-22
- Input: `data/examples/eligibility_criteria_1.json`
- Rules evaluated: 5
- Total violations: 0

## Rules

| Rule | Severity | Scope | Description |
| --- | --- | --- | --- |
| `USDM-REQ-001` | error | `StudyVersion` | StudyVersion must have at least one study identifier (studyIdentifiers, cardinality 1..*) |
| `USDM-REQ-002` | error | `StudyVersion` | StudyVersion must have at least one study title (titles, cardinality 1..*) |
| `USDM-REQ-003` | error | `StudyArm` | StudyArm must have a type code (type, cardinality 1) |
| `USDM-REQ-004` | error | `Encounter` | Encounter must have a non-empty name (name, cardinality 1) |
| `USDM-REQ-005` | error | `InterventionalStudyDesign` | InterventionalStudyDesign must have an intervention model code (model, cardinality 1) |

No violations found.
