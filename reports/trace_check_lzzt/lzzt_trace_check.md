# trace-check report

- Generated: 2026-11-10T19:08:04Z (usdm-toolkit 0.1.0)
- USDM: `usdm/CDISC_Pilot_Study_v4.json`
- SDTM: `sdtm`
- Findings: **0 error(s), 31 warning(s), 6 info**
- Rules run: 22, skipped: 0

| Rule | Severity | Category | Message | USDM | SDTM | Count |
|---|---|---|---|---|---|---|
| TC-SOA-002 | warning | Schedule of Activities | HBA1C planned at Week 2, Week 4, Week 12, Week 16, Week 20, Week 24, Week 26 but no LB records at that visit | BC Hemoglobin A1C Concentration in Blood | LBTESTCD='HBA1C' | 7 |
| TC-SV-001 | warning | Subject Data | SV visit 'AMBUL ECG PLACEMENT' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='AMBUL ECG PLACEMENT' | 208 |
| TC-SV-001 | warning | Subject Data | SV visit 'AMBUL ECG REMOVAL' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='AMBUL ECG REMOVAL' | 203 |
| TC-SV-001 | warning | Subject Data | SV visit 'WEEK 14 (T)' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='WEEK 14 (T)' | 141 |
| TC-SV-001 | warning | Subject Data | SV visit 'WEEK 22 (T)' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='WEEK 22 (T)' | 112 |
| TC-SV-001 | warning | Subject Data | SV visit 'AE FOLLOW-UP' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='AE FOLLOW-UP' | 74 |
| TC-SV-001 | warning | Subject Data | SV visit 'RETRIEVAL' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='RETRIEVAL' | 38 |
| TC-SV-001 | warning | Subject Data | SV visit 'WEEK 10 (T)' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='WEEK 10 (T)' | 156 |
| TC-SV-001 | warning | Subject Data | SV visit 'WEEK 18 (T)' is not a protocol encounter | StudyDesign.encounters | SV.VISIT='WEEK 18 (T)' | 124 |
| TC-TA-003 | warning | Trial Design | Protocol epoch 'Treatment Two' is not used in TA.EPOCH | StudyEpoch 'Treatment Two' | TA.EPOCH | 1 |
| TC-TA-003 | warning | Trial Design | Protocol epoch 'Treatment Three' is not used in TA.EPOCH | StudyEpoch 'Treatment Three' | TA.EPOCH | 1 |
| TC-TA-003 | warning | Trial Design | Protocol epoch 'Follow Up' is not used in TA.EPOCH | StudyEpoch 'Follow Up' | TA.EPOCH | 1 |
| TC-TA-004 | warning | Trial Design | Element sequence for arm 'Placebo' differs: protocol [Screening > Placebo > Follow up] vs TA [Screen > Placebo] | StudyArm 'Placebo' cells | TA.ARM='Placebo' | 1 |
| TC-TA-004 | warning | Trial Design | Element sequence for arm 'Xanomeline Low Dose' differs: protocol [Screening > Low > Follow up] vs TA [Screen > Low] | StudyArm 'Xanomeline Low Dose' cells | TA.ARM='Xanomeline Low Dose' | 1 |
| TC-TA-004 | warning | Trial Design | Element sequence for arm 'Xanomeline High Dose' differs: protocol [Screening > High - Start > High - Middle > High - End > Follow up] vs TA [Screen > High_Start > High_Middle > High_End] | StudyArm 'Xanomeline High Dose' cells | TA.ARM='Xanomeline High Dose' | 1 |
| TC-TI-002 | warning | Trial Design | Exclusion criterion 24: TI text differs from protocol (similarity 0.74). Protocol: 'A history within the last 5 years of a serious infectious disease including a) Neurosyphilis b) Meningitis c) Encephalit' | EligibilityCriterion EligibilityCriterion_24 | TI.IETESTCD='EXCL24' | 1 |
| TC-TI-002 | warning | Trial Design | Exclusion criterion 25: TI text differs from protocol (similarity 0.58). Protocol: 'A history within the last 5 years of a primary or recurrent malignant disease with the exception of resected cutaneous s' | EligibilityCriterion EligibilityCriterion_25 | TI.IETESTCD='EXCL25' | 1 |
| TC-TI-002 | warning | Trial Design | Exclusion criterion 29: TI text differs from protocol (similarity 0.31). Protocol: 'Positive syphilis screening. Positive syphilis screening. As determined by positive RPR followed up by confirmatory FTA-' | EligibilityCriterion EligibilityCriterion_29 | TI.IETESTCD='EXCL29' | 1 |
| TC-TI-002 | warning | Trial Design | Exclusion criterion 30: TI text differs from protocol (similarity 0.43). Protocol: 'Glycosylated hemoglobin (A1C). Required only on patients with known diabetes mellitus or random blood sugar >200 on scre' | EligibilityCriterion EligibilityCriterion_30 | TI.IETESTCD='EXCL30' | 1 |
| TC-TI-002 | warning | Trial Design | Exclusion criterion 31: TI text differs from protocol (similarity 0.65). Protocol: 'Treatment with the following medications within the specified washout periods prior to enrollment and during the study:' | EligibilityCriterion EligibilityCriterion_31 | TI.IETESTCD='EXCL31' | 1 |
| TC-TS-001 | warning | Trial Summary | TS SPONSOR 'CDISCPILOT01' does not match protocol value 'LILLY' | Sponsor organization name = 'LILLY' | TS.TSPARMCD='SPONSOR' TSVAL='CDISCPILOT01' | 1 |
| TC-TS-002 | warning | Trial Summary | TS OBJPRIM is not a protocol primary objective (best similarity 0.14): 'To document the safety profile of the xanomeline TTS.' | StudyDesign.objectives (primary) | TS.TSPARMCD='OBJPRIM' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'AMBUL ECG PLACEMENT' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='AMBUL ECG PLACEMENT' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'AMBUL ECG REMOVAL' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='AMBUL ECG REMOVAL' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'WEEK 10 (T)' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='WEEK 10 (T)' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'WEEK 14 (T)' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='WEEK 14 (T)' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'WEEK 18 (T)' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='WEEK 18 (T)' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'WEEK 22 (T)' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='WEEK 22 (T)' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'AE FOLLOW-UP' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='AE FOLLOW-UP' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'RETRIEVAL' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='RETRIEVAL' | 1 |
| TC-TV-002 | warning | Trial Design | TV visit 'Rash followup' is not a protocol encounter | StudyDesign.encounters | TV.VISIT='Rash followup' | 1 |
| TC-DM-002 | info | Subject Data | 12 subject(s) received a different arm than planned (Xan_Hi->Xan_Lo); confirm against protocol deviations and the reviewer's guide | StudyDesign.arms | DM.ARMCD vs DM.ACTARMCD | 12 |
| TC-SE-001 | info | Subject Data | Element matched approximately (score 0.85); confirm the labels refer to the same thing | Screening | Screen | 1 |
| TC-SOA-000 | info | Schedule of Activities | 10 scheduled biomedical concept(s) have no SDTM mapping and were not checked: Informed Consent (C16735); Sex (C28421); Race (C17049); Physical Examination Finding (C83119); Medical History (C83119); Alcohol Use (C81229); Caffeine Use (C201990); ECG Measurement (C62085); Concomitant Medications (C83056); ADAS-Cog (C100247) | biomedicalConcepts | (bc map) | 10 |
| TC-TE-001 | info | Trial Design | Element matched approximately (score 0.85); confirm the labels refer to the same thing | Screening | Screen | 1 |
| TC-TI-002 | info | Trial Design | 13 TI criterion text(s) are abbreviations of the protocol text (IETEST is limited to 200 characters); confirm nothing material was dropped: INCL02, INCL08, EXCL12, EXCL14, EXCL16, EXCL17, EXCL18, EXCL19, EXCL20, EXCL21, EXCL22, EXCL27, EXCL28 | eligibilityCriterionItems | TI.IETEST | 13 |
| TC-TS-001 | info | Trial Summary | TS has no REGID although the protocol defines it | Registry study identifier = 'NCT12345678' | TS.TSPARMCD='REGID' | 1 |
