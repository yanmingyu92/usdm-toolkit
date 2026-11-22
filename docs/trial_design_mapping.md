# trial-design: USDM v4.0 JSON → SDTM Trial Design mapping

The `trial-design` module converts a USDM v4.0 study-definition JSON (as
produced by the DDF-RA API / the `usdm` reference package) into five SDTM
Trial Design domain datasets, one CSV per domain: `TS`, `TA`, `TE`, `TV`,
`TI`.

Rows marked **[ASSUMPTION]** are pragmatic choices not dictated by either
standard; verify them against your SDTM IG conformance requirements.

## General

| Decision | Detail |
| --- | --- |
| Scope | First entry of `study.versions[*]`, first entry of `studyDesigns[*]` **[ASSUMPTION]** |
| `STUDYID` | Sponsor-issued `StudyIdentifier.text`: the identifier whose scope organisation's type decode does **not** contain "Registry"; falls back to the first identifier, then `study.name` **[ASSUMPTION]** |
| Code decoding | USDM `Code.decode`; for `AliasCode` the `standardCode.decode` is used |
| Sequence ordering | `StudyEpoch` / `Encounter` order follows the `previousId`/`nextId` linked list; unlinked nodes are appended in file order |
| Stated codes | USDM v4.0 has no attribute for `ARMCD`, `ETCD` or `VISITNUM`. When a `StudyArm`, `StudyElement` or `Encounter` carries an `ExtensionAttribute` with a non-empty `valueString` whose `url` ends in `/ARMCD`, `/ETCD` or `/VISITNUM` (last path segment, case-insensitive; the namespace is not checked), that value is used; otherwise the value is derived as described below |

## TS — Trial Summary

`TSPARMCD` / `TSPARM` are terms of the SDTM CT codelists TSPARMCD (C66738)
and TSPARM (C67152), checked against CDISC SDTM Controlled Terminology
2026-09-25 (NCI EVS). `STUDYID` is a column of every row, not a parameter.
A parameter with no value in the study is omitted. `TSSEQ` numbers the
values within one `TSPARMCD` (1, 2, …); with one value per parameter every
row has `TSSEQ = 1`.

`TSVAL` is the USDM decode, i.e. the NCI preferred term (for example
"Double Blind Study"), not the CDISC submission value ("DOUBLE BLIND").
Mapping one to the other needs the CT itself and is not done
**[ASSUMPTION]**.

| TSPARMCD | TSPARM | USDM source path |
| --- | --- | --- |
| TITLE | Trial Title | `versions[0].titles[*].text` where `type.decode` contains "Official", else "Brief", else first title **[ASSUMPTION]** |
| SPONSOR | Clinical Study Sponsor | `versions[0].organizations[*].name` of the organisation that issued STUDYID |
| REGID | Registry Identifier | `StudyIdentifier.text` whose scope organisation type decode contains "Registry" (e.g. ClinicalTrials.gov) **[ASSUMPTION]** |
| TPHASE | Trial Phase Classification | `studyDesigns[0].studyPhase.standardCode.decode` |
| INTMODEL | Intervention Model | `studyDesigns[0].model.decode` |
| TBLIND | Trial Blinding Schema | `studyDesigns[0].blindingSchema.standardCode.decode` |
| STYPE | Study Type | `studyDesigns[0].studyType.decode` |
| PLANSUB | Planned Number of Subjects | `studyDesigns[0].population.plannedEnrollmentNumber.value` |

## TA — Trial Arms

One row per (arm, epoch, element) found in the `studyCells` matrix.

| SDTM variable | USDM source path | Note |
| --- | --- | --- |
| ARMCD | stated code (see "General"), else derived from `arms[*].name` | Derivation: uppercased alphanumeric, ≤8 chars, numeric suffix on collision (also with stated codes) **[ASSUMPTION]** |
| ARM | `arms[*].name` | |
| TAETORD | running order per arm | Elements in epoch-chain order, then `StudyCell.elementIds` order |
| ETCD | stated code (see "General"), else derived from `elements[*].name` | Derivation: uppercased alphanumeric, ≤8 chars, numeric suffix on collision (also with stated codes) **[ASSUMPTION]** |
| ELEMENT | `elements[*].name` | |
| EPOCH | `epochs[*].name` | Epoch of the `StudyCell` |

## TE — Trial Elements

| SDTM variable | USDM source path | Note |
| --- | --- | --- |
| ETCD | as in TA | Same codes as TA **[ASSUMPTION]** |
| ELEMENT | `elements[*].name` | |
| TESTRL | `elements[*].transitionStartRule.text` | |
| TEENRL | `elements[*].transitionEndRule.text` | |

## TV — Trial Visits

| SDTM variable | USDM source path | Note |
| --- | --- | --- |
| VISITNUM | stated `VISITNUM` (see "General"), numeric, integers written without ".0"; else position (1-based) of the `Encounter` in the `previousId`/`nextId` chain | A stated value that is not a number falls back to the position |
| VISIT | `encounters[*].name` | |

`VISITDY` is not populated: USDM timing values live on schedule-timeline
timings rather than on encounters, and deriving nominal days requires
resolving `ScheduleTimeline`/`Timing` graphs — roadmap item.

## TI — Trial Inclusion/Exclusion Criteria

| SDTM variable | USDM source path | Note |
| --- | --- | --- |
| IETESTCD | `INCL`/`EXCL` prefix + `eligibilityCriteria[*].identifier` zero-padded to 3 | Prefix from the category split below **[ASSUMPTION]** |
| IETEST | text of the `EligibilityCriterionItem` referenced by `criterionItemId`; falls back to criterion `description`/`name` | |
| IECAT | `INCLUSION` / `EXCLUSION` from `eligibilityCriteria[*].category.decode` ("EXCL" substring test) | **[ASSUMPTION]** |
