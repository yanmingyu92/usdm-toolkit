# usdm-toolkit

An open-source toolchain for working with the CDISC **USDM** (Unified Study
Definitions Model) deliverables published in
[cdisc-org/DDF-RA](https://github.com/cdisc-org/DDF-RA).

The goal of the project is to make USDM easier to adopt in real systems:
validators, consistency checkers, converters and documentation generators that
operate directly on the published deliverables (`dataStructure.yml`,
`USDM_CT.xlsx`, the API specs, and friends).

> **Disclaimer.** usdm-toolkit is an independent, community-driven open-source
> project. It is **not** developed, endorsed, or reviewed by CDISC or the
> CDISC DDF team, and it is not part of the official DDF-RA deliverables.
> The USDM model files and controlled terminology remain the property of
> CDISC and are subject to the CDISC license terms; this project merely reads
> the published files. Any findings reported here are the tool author's
> interpretation and should be verified against the official CDISC sources
> before being relied upon.

## Capability matrix (v0.1)

| Module | Input | Output | Purpose |
| --- | --- | --- | --- |
| `ct-align` | `dataStructure.yml` + `USDM_CT.xlsx` | Markdown/JSON report | Consistency checker between the model export and the controlled terminology (C-codes, preferred terms, definitions, value lists, coverage gaps) |
| `trial-design` | USDM v4.0 study JSON | `TS`/`TA`/`TE`/`TV`/`TI` CSVs | Generate SDTM Trial Design domain datasets from a USDM study definition |
| `rules` | USDM study JSON + YAML rule library | Markdown/JSON violations report | Execute conformance rules (JSONata expressions) against a USDM JSON instance |

## Installation

```bash
python -m venv .venv
# Windows (Git Bash):
source .venv/Scripts/activate
# Linux/macOS:
# source .venv/bin/activate
pip install -e .[dev]        # or: pip install -r requirements.txt
```

Requires Python 3.10+.

## Usage

### ct-align — model vs. controlled terminology consistency

```bash
python -m usdm_toolkit.cli ct-align \
    --yaml data/source/dataStructure.yml \
    --ct data/source/USDM_CT.xlsx \
    --out reports/ct_align_report.md --format md
```

- `--format md` (default) writes a Markdown report; `--format json` emits the
  findings as JSON for downstream processing.
- Exit code is `1` when error-severity findings exist, `0` otherwise, so the
  checker can be wired into CI.

### trial-design — USDM JSON → SDTM Trial Design

```bash
python -m usdm_toolkit.cli trial-design \
    --input data/examples/complex_1.json \
    --out reports/trial_design_complex_1
```

Writes one CSV per domain (`TS.csv`, `TA.csv`, `TE.csv`, `TV.csv`, `TI.csv`)
into the output directory. The full USDM-path → SDTM-variable mapping,
including flagged assumptions, is documented in
[`docs/trial_design_mapping.md`](docs/trial_design_mapping.md).

### rules — conformance rule executor

```bash
python -m usdm_toolkit.cli rules \
    --input data/examples/complex_1.json \
    --out reports/rules_complex_1.md --format md
```

- Rules are YAML files with `id`, `description`, `severity`, `scope` (the
  USDM `instanceType` a rule applies to) and `expression` (a JSONata boolean;
  falsy/undefined = violation). The bundled starter library lives in
  [`src/usdm_toolkit/rules/library/`](src/usdm_toolkit/rules/library/) and is
  derived from the required (`Cardinality = 1` / `1..*`) attributes in
  `dataStructure.yml`.
- `--rules-dir` points at a custom rule directory; without it the bundled
  library is used.
- Exit code is `1` when error-severity violations exist, `0` otherwise.

## What ct-align checks

| Rule | Severity | Meaning |
| --- | --- | --- |
| `CLASS_NOT_IN_CT` | warning | Class in `dataStructure.yml` has no entity row in `USDM_CT.xlsx` |
| `CLASS_CCODE_MISMATCH` / `CLASS_TERM_MISMATCH` / `CLASS_DEFINITION_MISMATCH` | error | Class-level C-code / preferred term / definition differs |
| `ATTR_CCODE_MISMATCH` | error | Attribute C-code differs; the report also names the CT row that actually owns the YAML's code |
| `ATTR_TERM_MISMATCH` / `ATTR_DEFINITION_MISMATCH` | error | Attribute preferred term / definition differs |
| `ATTR_NOT_IN_CT` | warning | YAML attribute carries a C-code but has no CT row |
| `CCODE_NOT_IN_CT` | error | YAML references a C-code that occurs nowhere in the CT workbook |
| `VALUE_LIST_TYPE_MISMATCH` | warning | CT declares a value list but the YAML attribute is not `Code`-typed (or vice versa) |
| `CLASSIFICATION_WITHOUT_VALUE_LIST` | warning | Definition follows the "A characterization or classification of ..." pattern but `Has Value List = N` |
| `CT_ATTR_NOT_IN_YAML` | info | CT attribute row with no C-code-carrying counterpart in the YAML (coverage gap) |

## Source data

The files under `data/source/` are pinned to DDF-RA tag `v4.0.0`; see
[`data/source/SOURCE.md`](data/source/SOURCE.md) for provenance. The example
USDM JSON studies under `data/examples/` come from the integration-test
fixtures of the upstream [cdisc-org/usdm](https://github.com/cdisc-org/usdm)
package (USDM model v4.0.0); see
[`data/examples/SOURCE.md`](data/examples/SOURCE.md).

A full ct-align run against the v4.0.0 files is documented in
[`reports/ct_align_report_2026-10-22.md`](reports/ct_align_report_2026-10-22.md),
including a cross-check against DDF-RA issues
[#716](https://github.com/cdisc-org/DDF-RA/issues/716),
[#717](https://github.com/cdisc-org/DDF-RA/issues/717) and
[#718](https://github.com/cdisc-org/DDF-RA/issues/718), all of which the tool
reproduces exactly. End-to-end `trial-design` and `rules` runs against the
example studies are under `reports/trial_design_*/` and `reports/rules_*.md`.

## Development

```bash
pytest            # run the test suite (synthetic fixtures + example smoke tests)
```

## Roadmap ideas

- `ct-align` diff mode for release-to-release CT deltas (`CT_DELTA_*.xlsx`)
- `rules`: import the DDF-RA CORE-style rule deliverables
  (`Deliverables/RULES`) into the YAML rule format
- SDR API connector (fetch study definitions directly from a Study
  Definitions Repository instead of local JSON files)
- `trial-design`: derive `VISITDY`/timing outputs from `ScheduleTimeline`
  graphs; multi-design studies
- validators for USDM JSON instances against `dataStructure.yml`
- export helpers (RDF/OWL, data dictionaries)

Contributions welcome. Please keep checks deterministic and backed by the
published source files — no hand-maintained finding lists.
