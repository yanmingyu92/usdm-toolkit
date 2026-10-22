# ct-align consistency report

- Report date: 2026-10-22
- Model file: `data/source/dataStructure.yml`
- CT file: `data/source/USDM_CT.xlsx`
- Total findings: 263

## Summary by rule

| Rule | Severity | Count |
| --- | --- | --- |
| `CLASS_NOT_IN_CT` | warning | 2 |
| `ATTR_CCODE_MISMATCH` | error | 27 |
| `ATTR_TERM_MISMATCH` | error | 27 |
| `ATTR_DEFINITION_MISMATCH` | error | 27 |
| `CT_ATTR_NOT_IN_YAML` | info | 172 |
| `CLASSIFICATION_WITHOUT_VALUE_LIST` | warning | 1 |
| `VALUE_LIST_TYPE_MISMATCH` | warning | 7 |

## Classes in dataStructure.yml without a CT entity row (`CLASS_NOT_IN_CT`, 2)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| ExtensionAttribute | - | - | - | - | Class 'ExtensionAttribute' has no entity row in USDM_CT.xlsx (C-code in YAML: none) |
| ExtensionClass | - | - | - | - | Class 'ExtensionClass' has no entity row in USDM_CT.xlsx (C-code in YAML: none) |

## Attribute-level C-code mismatches (`ATTR_CCODE_MISMATCH`, 27)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| Identifier.text | C215581 | C215450 | Administrable Product Identifier Text | Identifier Text | Identifier.text: YAML C-code C215581 != CT C-code C215450 (CT row 470); YAML code is the CT row of AdministrableProductIdentifier.text |
| PopulationDefinition.name | C207544 | C207520 | Study Cohort Name | Population Definition Name | PopulationDefinition.name: YAML C-code C207544 != CT C-code C207520 (CT row 399); YAML code is the CT row of StudyCohort.name |
| PopulationDefinition.label | C207543 | C207519 | Study Cohort Label | Population Definition Label | PopulationDefinition.label: YAML C-code C207543 != CT C-code C207519 (CT row 401); YAML code is the CT row of StudyCohort.label |
| PopulationDefinition.description | C207542 | C207517 | Study Cohort Description | Population Definition Description | PopulationDefinition.description: YAML C-code C207542 != CT C-code C207517 (CT row 400); YAML code is the CT row of StudyCohort.description |
| PopulationDefinition.plannedSex | C207541 | C207523 | Study Cohort Planned Sex | Population Definition Planned Sex | PopulationDefinition.plannedSex: YAML C-code C207541 != CT C-code C207523 (CT row 402); YAML code is the CT row of StudyCohort.plannedSex |
| PopulationDefinition.includesHealthySubjects | C207480 | C207518 | Study Cohort Includes Healthy Subjects Indicator | Population Definition Includes Healthy Subjects Indicator | PopulationDefinition.includesHealthySubjects: YAML C-code C207480 != CT C-code C207518 (CT row 404); YAML code is the CT row of StudyCohort.includesHealthySubjects |
| PopulationDefinition.plannedAge | C207545 | C207701 | Study Cohort Planned Age | Population Definition Planned Age | PopulationDefinition.plannedAge: YAML C-code C207545 != CT C-code C207701 (CT row 403); YAML code is the CT row of StudyCohort.plannedAge |
| PopulationDefinition.plannedCompletionNumber | C207546 | C207521 | Study Cohort Planned Completion Number | Population Definition Planned Completion Number | PopulationDefinition.plannedCompletionNumber: YAML C-code C207546 != CT C-code C207521 (CT row 405); YAML code is the CT row of StudyCohort.plannedCompletionNumber |
| PopulationDefinition.plannedEnrollmentNumber | C207702 | C207522 | Study Cohort Planned Enrollment Number | Population Definition Planned Enrollment Number | PopulationDefinition.plannedEnrollmentNumber: YAML C-code C207702 != CT C-code C207522 (CT row 406); YAML code is the CT row of StudyCohort.plannedEnrollmentNumber |
| PopulationDefinition.notes | C215547 | C215551 | Study Cohort Notes | Population Definition Notes | PopulationDefinition.notes: YAML C-code C215547 != CT C-code C215551 (CT row 408); YAML code is the CT row of StudyCohort.notes |
| ScheduledInstance.name | C207533 | C207455 | Scheduled Activity Instance Name | Scheduled Instance Name | ScheduledInstance.name: YAML C-code C207533 != CT C-code C207455 (CT row 243); YAML code is the CT row of ScheduledActivityInstance.name |
| ScheduledInstance.label | C207532 | C207454 | Scheduled Activity Instance Label | Scheduled Instance Label | ScheduledInstance.label: YAML C-code C207532 != CT C-code C207454 (CT row 245); YAML code is the CT row of ScheduledActivityInstance.label |
| ScheduledInstance.description | C207531 | C207453 | Scheduled Activity Instance Description | Scheduled Instance Description | ScheduledInstance.description: YAML C-code C207531 != CT C-code C207453 (CT row 244); YAML code is the CT row of ScheduledActivityInstance.description |
| StudyDesign.name | C215626 | C201338 | Interventional Study Design Name | Study Design Name | StudyDesign.name: YAML C-code C215626 != CT C-code C201338 (CT row 36); YAML code is the CT row of InterventionalStudyDesign.name |
| StudyDesign.label | C215628 | C207548 | Interventional Study Design Label | Study Design Label | StudyDesign.label: YAML C-code C215628 != CT C-code C207548 (CT row 39); YAML code is the CT row of InterventionalStudyDesign.label |
| StudyDesign.description | C215627 | C147139 | Interventional Study Design Description | Study Design Description | StudyDesign.description: YAML C-code C215627 != CT C-code C147139 (CT row 37); YAML code is the CT row of InterventionalStudyDesign.description |
| StudyDesign.rationale | C215629 | C142705 | Interventional Study Design Rationale | Study Design Rationale | StudyDesign.rationale: YAML C-code C215629 != CT C-code C142705 (CT row 38); YAML code is the CT row of InterventionalStudyDesign.rationale |
| StudyDesign.therapeuticAreas | C215633 | C101302 | Interventional Study Design Therapeutic Areas | Therapeutic Areas | StudyDesign.therapeuticAreas: YAML C-code C215633 != CT C-code C101302 (CT row 35); YAML code is the CT row of InterventionalStudyDesign.therapeuticAreas |
| StudyDesign.studyType | C215631 | C142175 | Interventional Study Design Study Type | Study Type | StudyDesign.studyType: YAML C-code C215631 != CT C-code C142175 (CT row 41); YAML code is the CT row of InterventionalStudyDesign.studyType |
| StudyDesign.characteristics | C215632 | C207547 | Interventional Study Design Characteristics | Study Design Characteristic | StudyDesign.characteristics: YAML C-code C215632 != CT C-code C207547 (CT row 40); YAML code is the CT row of InterventionalStudyDesign.characteristics |
| StudyDesign.studyPhase | C215630 | C48281 | Interventional Study Design Study Phase | Trial Phase | StudyDesign.studyPhase: YAML C-code C215630 != CT C-code C48281 (CT row 42); YAML code is the CT row of InterventionalStudyDesign.studyPhase |
| StudyDesign.notes | C215634 | C215508 | Interventional Study Design Notes | Study Design Notes | StudyDesign.notes: YAML C-code C215634 != CT C-code C215508 (CT row 34); YAML code is the CT row of InterventionalStudyDesign.notes |
| SyntaxTemplate.name | C207477 | C207577 | Characteristic Name | Syntax Template Name | SyntaxTemplate.name: YAML C-code C207477 != CT C-code C207577 (CT row 284); YAML code is the CT row of Characteristic.name |
| SyntaxTemplate.label | C207476 | C207576 | Characteristic Label | Syntax Template Label | SyntaxTemplate.label: YAML C-code C207476 != CT C-code C207576 (CT row 287); YAML code is the CT row of Characteristic.label |
| SyntaxTemplate.description | C207475 | C207575 | Characteristic Description | Syntax Template Description | SyntaxTemplate.description: YAML C-code C207475 != CT C-code C207575 (CT row 286); YAML code is the CT row of Characteristic.description |
| SyntaxTemplate.text | C207478 | C207578 | Characteristic Text | Syntax Template Text | SyntaxTemplate.text: YAML C-code C207478 != CT C-code C207578 (CT row 285); YAML code is the CT row of Characteristic.text |
| SyntaxTemplate.notes | C215548 | C215536 | Characteristic Notes | Syntax Template Notes | SyntaxTemplate.notes: YAML C-code C215548 != CT C-code C215536 (CT row 289); YAML code is the CT row of Characteristic.notes |

## Attribute-level preferred term mismatches (`ATTR_TERM_MISMATCH`, 27)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| Identifier.text | C215581 | C215450 | Administrable Product Identifier Text | Identifier Text | Identifier.text: Preferred Term differs (YAML: 'Administrable Product Identifier Text', CT row 470: 'Identifier Text') |
| PopulationDefinition.name | C207544 | C207520 | Study Cohort Name | Population Definition Name | PopulationDefinition.name: Preferred Term differs (YAML: 'Study Cohort Name', CT row 399: 'Population Definition Name') |
| PopulationDefinition.label | C207543 | C207519 | Study Cohort Label | Population Definition Label | PopulationDefinition.label: Preferred Term differs (YAML: 'Study Cohort Label', CT row 401: 'Population Definition Label') |
| PopulationDefinition.description | C207542 | C207517 | Study Cohort Description | Population Definition Description | PopulationDefinition.description: Preferred Term differs (YAML: 'Study Cohort Description', CT row 400: 'Population Definition Description') |
| PopulationDefinition.plannedSex | C207541 | C207523 | Study Cohort Planned Sex | Population Definition Planned Sex | PopulationDefinition.plannedSex: Preferred Term differs (YAML: 'Study Cohort Planned Sex', CT row 402: 'Population Definition Planned Sex') |
| PopulationDefinition.includesHealthySubjects | C207480 | C207518 | Study Cohort Includes Healthy Subjects Indicator | Population Definition Includes Healthy Subjects Indicator | PopulationDefinition.includesHealthySubjects: Preferred Term differs (YAML: 'Study Cohort Includes Healthy Subjects Indicator', CT row 404: 'Population Definition Includes Healthy Subjects Indicator') |
| PopulationDefinition.plannedAge | C207545 | C207701 | Study Cohort Planned Age | Population Definition Planned Age | PopulationDefinition.plannedAge: Preferred Term differs (YAML: 'Study Cohort Planned Age', CT row 403: 'Population Definition Planned Age') |
| PopulationDefinition.plannedCompletionNumber | C207546 | C207521 | Study Cohort Planned Completion Number | Population Definition Planned Completion Number | PopulationDefinition.plannedCompletionNumber: Preferred Term differs (YAML: 'Study Cohort Planned Completion Number', CT row 405: 'Population Definition Planned Completion Number') |
| PopulationDefinition.plannedEnrollmentNumber | C207702 | C207522 | Study Cohort Planned Enrollment Number | Population Definition Planned Enrollment Number | PopulationDefinition.plannedEnrollmentNumber: Preferred Term differs (YAML: 'Study Cohort Planned Enrollment Number', CT row 406: 'Population Definition Planned Enrollment Number') |
| PopulationDefinition.notes | C215547 | C215551 | Study Cohort Notes | Population Definition Notes | PopulationDefinition.notes: Preferred Term differs (YAML: 'Study Cohort Notes', CT row 408: 'Population Definition Notes') |
| ScheduledInstance.name | C207533 | C207455 | Scheduled Activity Instance Name | Scheduled Instance Name | ScheduledInstance.name: Preferred Term differs (YAML: 'Scheduled Activity Instance Name', CT row 243: 'Scheduled Instance Name') |
| ScheduledInstance.label | C207532 | C207454 | Scheduled Activity Instance Label | Scheduled Instance Label | ScheduledInstance.label: Preferred Term differs (YAML: 'Scheduled Activity Instance Label', CT row 245: 'Scheduled Instance Label') |
| ScheduledInstance.description | C207531 | C207453 | Scheduled Activity Instance Description | Scheduled Instance Description | ScheduledInstance.description: Preferred Term differs (YAML: 'Scheduled Activity Instance Description', CT row 244: 'Scheduled Instance Description') |
| StudyDesign.name | C215626 | C201338 | Interventional Study Design Name | Study Design Name | StudyDesign.name: Preferred Term differs (YAML: 'Interventional Study Design Name', CT row 36: 'Study Design Name') |
| StudyDesign.label | C215628 | C207548 | Interventional Study Design Label | Study Design Label | StudyDesign.label: Preferred Term differs (YAML: 'Interventional Study Design Label', CT row 39: 'Study Design Label') |
| StudyDesign.description | C215627 | C147139 | Interventional Study Design Description | Study Design Description | StudyDesign.description: Preferred Term differs (YAML: 'Interventional Study Design Description', CT row 37: 'Study Design Description') |
| StudyDesign.rationale | C215629 | C142705 | Interventional Study Design Rationale | Study Design Rationale | StudyDesign.rationale: Preferred Term differs (YAML: 'Interventional Study Design Rationale', CT row 38: 'Study Design Rationale') |
| StudyDesign.therapeuticAreas | C215633 | C101302 | Interventional Study Design Therapeutic Areas | Therapeutic Areas | StudyDesign.therapeuticAreas: Preferred Term differs (YAML: 'Interventional Study Design Therapeutic Areas', CT row 35: 'Therapeutic Areas') |
| StudyDesign.studyType | C215631 | C142175 | Interventional Study Design Study Type | Study Type | StudyDesign.studyType: Preferred Term differs (YAML: 'Interventional Study Design Study Type', CT row 41: 'Study Type') |
| StudyDesign.characteristics | C215632 | C207547 | Interventional Study Design Characteristics | Study Design Characteristic | StudyDesign.characteristics: Preferred Term differs (YAML: 'Interventional Study Design Characteristics', CT row 40: 'Study Design Characteristic') |
| StudyDesign.studyPhase | C215630 | C48281 | Interventional Study Design Study Phase | Trial Phase | StudyDesign.studyPhase: Preferred Term differs (YAML: 'Interventional Study Design Study Phase', CT row 42: 'Trial Phase') |
| StudyDesign.notes | C215634 | C215508 | Interventional Study Design Notes | Study Design Notes | StudyDesign.notes: Preferred Term differs (YAML: 'Interventional Study Design Notes', CT row 34: 'Study Design Notes') |
| SyntaxTemplate.name | C207477 | C207577 | Characteristic Name | Syntax Template Name | SyntaxTemplate.name: Preferred Term differs (YAML: 'Characteristic Name', CT row 284: 'Syntax Template Name') |
| SyntaxTemplate.label | C207476 | C207576 | Characteristic Label | Syntax Template Label | SyntaxTemplate.label: Preferred Term differs (YAML: 'Characteristic Label', CT row 287: 'Syntax Template Label') |
| SyntaxTemplate.description | C207475 | C207575 | Characteristic Description | Syntax Template Description | SyntaxTemplate.description: Preferred Term differs (YAML: 'Characteristic Description', CT row 286: 'Syntax Template Description') |
| SyntaxTemplate.text | C207478 | C207578 | Characteristic Text | Syntax Template Text | SyntaxTemplate.text: Preferred Term differs (YAML: 'Characteristic Text', CT row 285: 'Syntax Template Text') |
| SyntaxTemplate.notes | C215548 | C215536 | Characteristic Notes | Syntax Template Notes | SyntaxTemplate.notes: Preferred Term differs (YAML: 'Characteristic Notes', CT row 289: 'Syntax Template Notes') |

## Attribute-level definition mismatches (`ATTR_DEFINITION_MISMATCH`, 27)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| Identifier.text | C215581 | C215450 | An instance of structured text that represents the administrable product. | An instance of structured text that represents the identifier. | Identifier.text: Definition differs between YAML and CT row 470 |
| PopulationDefinition.name | C207544 | C207520 | The literal identifier (i.e., distinctive designation) of the study cohort. | The literal identifier (i.e., distinctive designation) of the population definition. | PopulationDefinition.name: Definition differs between YAML and CT row 399 |
| PopulationDefinition.label | C207543 | C207519 | The short descriptive designation for the study cohort. | The short descriptive designation for the population definition. | PopulationDefinition.label: Definition differs between YAML and CT row 401 |
| PopulationDefinition.description | C207542 | C207517 | A narrative representation of the study cohort. | A narrative representation of the population definition. | PopulationDefinition.description: Definition differs between YAML and CT row 400 |
| PopulationDefinition.plannedSex | C207541 | C207523 | The protocol-defined sex within the study cohort. | The protocol-defined sex within the population definition. | PopulationDefinition.plannedSex: Definition differs between YAML and CT row 402 |
| PopulationDefinition.includesHealthySubjects | C207480 | C207518 | An indication as to whether the study cohort includes healthy subjects, that is, subjects without the disease or condition under study. | An indication as to whether the population definition includes healthy subjects, that is, subjects without the disease or condition under study. | PopulationDefinition.includesHealthySubjects: Definition differs between YAML and CT row 404 |
| PopulationDefinition.plannedAge | C207545 | C207701 | The anticipated age of subjects within the study cohort. | The anticipated age of subjects within the population definition. | PopulationDefinition.plannedAge: Definition differs between YAML and CT row 403 |
| PopulationDefinition.plannedCompletionNumber | C207546 | C207521 | The value representing the planned number of subjects that must complete the study in order to meet the objectives and endpoints of the study, within the study cohort. | The value representing the planned number of subjects that must complete the study in order to meet the objectives and endpoints of the study, within the population definition. | PopulationDefinition.plannedCompletionNumber: Definition differs between YAML and CT row 405 |
| PopulationDefinition.plannedEnrollmentNumber | C207702 | C207522 | The value representing the planned number of subjects to be entered in a clinical trial, within the study cohort. | The value representing the planned number of subjects to be entered in a clinical trial, within the population definition. | PopulationDefinition.plannedEnrollmentNumber: Definition differs between YAML and CT row 406 |
| PopulationDefinition.notes | C215547 | C215551 | A brief written record relevant to the study cohort. | A brief written record relevant to the population definition. | PopulationDefinition.notes: Definition differs between YAML and CT row 408 |
| ScheduledInstance.name | C207533 | C207455 | The literal identifier (i.e., distinctive designation) of the scheduled activity instance. | The literal identifier (i.e., distinctive designation) of the scheduled instance. | ScheduledInstance.name: Definition differs between YAML and CT row 243 |
| ScheduledInstance.label | C207532 | C207454 | The short descriptive designation for the scheduled activity instance. | The short descriptive designation for the scheduled instance. | ScheduledInstance.label: Definition differs between YAML and CT row 245 |
| ScheduledInstance.description | C207531 | C207453 | A narrative representation of the scheduled activity instance. | A narrative representation of the scheduled instance. | ScheduledInstance.description: Definition differs between YAML and CT row 244 |
| StudyDesign.name | C215626 | C201338 | The literal identifier (i.e., distinctive designation) of the interventional study design. | The literal identifier (i.e., distinctive designation) of the study design. | StudyDesign.name: Definition differs between YAML and CT row 36 |
| StudyDesign.label | C215628 | C207548 | The short descriptive designation for the interventional study design. | The short descriptive designation for the study design. | StudyDesign.label: Definition differs between YAML and CT row 39 |
| StudyDesign.description | C215627 | C147139 | A narrative representation of the interventional study design. | A narrative representation of the study design. | StudyDesign.description: Definition differs between YAML and CT row 37 |
| StudyDesign.rationale | C215629 | C142705 | Reason(s) for choosing the interventional study design. This may include reasons for the choice of control or comparator, as well as the scientific rationale for the study design. | Reason(s) for choosing the study design. This may include reasons for the choice of control or comparator, as well as the scientific rationale for the study design. | StudyDesign.rationale: Definition differs between YAML and CT row 38 |
| StudyDesign.therapeuticAreas | C215633 | C101302 | A categorization of a disease, disorder, or other condition based on common characteristics and often associated with a medical specialty focusing on research and development of specific therapeutic interventions for the purpose of treatment and prevention, which is associated with the interventional study design. | A categorization of a disease, disorder, or other condition based on common characteristics and often associated with a medical specialty focusing on research and development of specific therapeutic interventions for the purpose of treatment and prevention. | StudyDesign.therapeuticAreas: Definition differs between YAML and CT row 35 |
| StudyDesign.studyType | C215631 | C142175 | The study type associated with the interventional study design. | The nature of the investigation for which study information is being collected. (After clinicaltrials.gov) | StudyDesign.studyType: Definition differs between YAML and CT row 41 |
| StudyDesign.characteristics | C215632 | C207547 | The distinguishing qualities or prominent aspects of an interventional study design. | The distinguishing qualities or prominent aspect of a study design. | StudyDesign.characteristics: Definition differs between YAML and CT row 40 |
| StudyDesign.studyPhase | C215630 | C48281 | The study phase associated with the interventional study design. | A step in the clinical research and development of a therapy from initial clinical trials to post-approval studies. NOTE: Clinical trials are generally categorized into four (sometimes five) phases. A therapeutic intervention may be evaluated in two or more phases simultaneously in different trials, and some trials may overlap two different phases. [21 CFR section 312.21; After ICH Topic E8 NOTE FOR GUIDANCE ON GENERAL CONSIDERATIONS FOR CLINICAL TRIALS, CPMP/ICH/291/95 March 1998] | StudyDesign.studyPhase: Definition differs between YAML and CT row 42 |
| StudyDesign.notes | C215634 | C215508 | A brief written record relevant to the interventional study design. | A brief written record relevant to the study design. | StudyDesign.notes: Definition differs between YAML and CT row 34 |
| SyntaxTemplate.name | C207477 | C207577 | The literal identifier (i.e., distinctive designation) of the characteristic. | The literal identifier (i.e., distinctive designation) of the syntax template. | SyntaxTemplate.name: Definition differs between YAML and CT row 284 |
| SyntaxTemplate.label | C207476 | C207576 | The short descriptive designation for the characteristic. | The short descriptive designation for the syntax template. | SyntaxTemplate.label: Definition differs between YAML and CT row 287 |
| SyntaxTemplate.description | C207475 | C207575 | A narrative representation of the characteristic. | A narrative representation of the syntax template. | SyntaxTemplate.description: Definition differs between YAML and CT row 286 |
| SyntaxTemplate.text | C207478 | C207578 | An instance of structured text that represents the characteristic. | A structured text string containing prescribed text interspersed with user-defined parameter values. | SyntaxTemplate.text: Definition differs between YAML and CT row 285 |
| SyntaxTemplate.notes | C215548 | C215536 | A brief written record relevant to the characteristic. | A brief written record relevant to the syntax template. | SyntaxTemplate.notes: Definition differs between YAML and CT row 289 |

## CT rows without a YAML C-code counterpart (coverage) (`CT_ATTR_NOT_IN_YAML`, 172)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| Activity.bcCategories | - | - | - | - | Activity.bcCategories: CT row 130 (Relationship, None) missing from YAML |
| Activity.bcSurrogates | - | - | - | - | Activity.bcSurrogates: CT row 131 (Relationship, None) missing from YAML |
| Activity.biomedicalConcepts | - | - | - | - | Activity.biomedicalConcepts: CT row 129 (Relationship, None) missing from YAML |
| Activity.children | - | - | - | - | Activity.children: CT row 136 (Relationship, None) missing from YAML |
| Activity.definedProcedures | - | - | - | - | Activity.definedProcedures: CT row 128 (Relationship, None) has no C-code in YAML |
| Activity.next | - | - | - | - | Activity.next: CT row 133 (Relationship, None) missing from YAML |
| Activity.previous | - | - | - | - | Activity.previous: CT row 132 (Relationship, None) missing from YAML |
| Activity.timeline | - | - | - | - | Activity.timeline: CT row 134 (Relationship, None) missing from YAML |
| AdministrableProduct.identifiers | - | - | - | - | AdministrableProduct.identifiers: CT row 483 (Relationship, None) has no C-code in YAML |
| AdministrableProduct.ingredients | - | - | - | - | AdministrableProduct.ingredients: CT row 481 (Relationship, None) has no C-code in YAML |
| AdministrableProduct.properties | - | - | - | - | AdministrableProduct.properties: CT row 482 (Relationship, None) has no C-code in YAML |
| AdministrableProductIdentifier.scope | - | - | - | - | AdministrableProductIdentifier.scope: CT row 486 (Relationship, None) missing from YAML |
| Administration.administrableProduct | - | - | - | - | Administration.administrableProduct: CT row 373 (Relationship, None) missing from YAML |
| Administration.medicalDevice | - | - | - | - | Administration.medicalDevice: CT row 374 (Relationship, None) missing from YAML |
| AnalysisPopulation.subsetOf | - | - | - | - | AnalysisPopulation.subsetOf: CT row 164 (Relationship, None) missing from YAML |
| AssignedPerson.organization | - | - | - | - | AssignedPerson.organization: CT row 514 (Relationship, None) missing from YAML |
| BiomedicalConcept.properties | - | - | - | - | BiomedicalConcept.properties: CT row 190 (Relationship, None) has no C-code in YAML |
| BiomedicalConceptCategory.children | - | - | - | - | BiomedicalConceptCategory.children: CT row 219 (Relationship, None) missing from YAML |
| BiomedicalConceptCategory.members | - | - | - | - | BiomedicalConceptCategory.members: CT row 218 (Relationship, None) missing from YAML |
| BiomedicalConceptProperty.responseCodes | - | - | - | - | BiomedicalConceptProperty.responseCodes: CT row 198 (Relationship, None) has no C-code in YAML |
| Characteristic.dictionary | - | - | - | - | Characteristic.dictionary: CT row 396 (Relationship, None) missing from YAML |
| Condition.appliesTo | - | - | - | - | Condition.appliesTo: CT row 422 (Relationship, None) missing from YAML |
| Condition.context | - | - | - | - | Condition.context: CT row 421 (Relationship, None) missing from YAML |
| Condition.dictionary | - | - | - | - | Condition.dictionary: CT row 423 (Relationship, None) missing from YAML |
| ConditionAssignment.conditionTarget | - | - | - | - | ConditionAssignment.conditionTarget: CT row 438 (Relationship, None) missing from YAML |
| DocumentContentReference.appliesTo | - | - | - | - | DocumentContentReference.appliesTo: CT row 535 (Relationship, None) missing from YAML |
| EligibilityCriterion.criterionItem | - | - | - | - | EligibilityCriterion.criterionItem: CT row 304 (Relationship, None) missing from YAML |
| EligibilityCriterion.next | - | - | - | - | EligibilityCriterion.next: CT row 301 (Relationship, None) missing from YAML |
| EligibilityCriterion.previous | - | - | - | - | EligibilityCriterion.previous: CT row 302 (Relationship, None) missing from YAML |
| EligibilityCriterionItem.dictionary | - | - | - | - | EligibilityCriterionItem.dictionary: CT row 632 (Relationship, None) missing from YAML |
| Encounter.next | - | - | - | - | Encounter.next: CT row 125 (Relationship, None) missing from YAML |
| Encounter.previous | - | - | - | - | Encounter.previous: CT row 124 (Relationship, None) missing from YAML |
| Encounter.scheduledAt | - | - | - | - | Encounter.scheduledAt: CT row 123 (Relationship, None) missing from YAML |
| Encounter.transitionEndRule | - | - | - | - | Encounter.transitionEndRule: CT row 122 (Relationship, None) has no C-code in YAML |
| Encounter.transitionStartRule | - | - | - | - | Encounter.transitionStartRule: CT row 121 (Relationship, None) has no C-code in YAML |
| Endpoint.dictionary | - | - | - | - | Endpoint.dictionary: CT row 78 (Relationship, None) missing from YAML |
| Estimand.analysisPopulation | - | - | - | - | Estimand.analysisPopulation: CT row 149 (Relationship, None) missing from YAML |
| Estimand.intercurrentEvents | - | - | - | - | Estimand.intercurrentEvents: CT row 150 (Relationship, None) has no C-code in YAML |
| Estimand.interventions | - | - | - | - | Estimand.interventions: CT row 151 (Relationship, None) missing from YAML |
| Estimand.variableOfInterest | - | - | - | - | Estimand.variableOfInterest: CT row 152 (Relationship, None) missing from YAML |
| GovernanceDate.geographicScopes | - | - | - | - | GovernanceDate.geographicScopes: CT row 311 (Relationship, None) has no C-code in YAML |
| Identifier.scope | - | - | - | - | Identifier.scope: CT row 471 (Relationship, None) missing from YAML |
| Ingredient.substance | - | - | - | - | Ingredient.substance: CT row 507 (Relationship, None) has no C-code in YAML |
| IntercurrentEvent.dictionary | - | - | - | - | IntercurrentEvent.dictionary: CT row 172 (Relationship, None) missing from YAML |
| InterventionalStudyDesign.activities | - | - | - | - | InterventionalStudyDesign.activities: CT row 583 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.arms | - | - | - | - | InterventionalStudyDesign.arms: CT row 586 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.biospecimenRetentions | - | - | - | - | InterventionalStudyDesign.biospecimenRetentions: CT row 589 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.documentVersions | - | - | - | - | InterventionalStudyDesign.documentVersions: CT row 588 (Relationship, None) missing from YAML |
| InterventionalStudyDesign.elements | - | - | - | - | InterventionalStudyDesign.elements: CT row 587 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.eligibilityCriteria | - | - | - | - | InterventionalStudyDesign.eligibilityCriteria: CT row 590 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.encounters | - | - | - | - | InterventionalStudyDesign.encounters: CT row 582 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.epochs | - | - | - | - | InterventionalStudyDesign.epochs: CT row 585 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.estimands | - | - | - | - | InterventionalStudyDesign.estimands: CT row 579 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.indications | - | - | - | - | InterventionalStudyDesign.indications: CT row 577 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.objectives | - | - | - | - | InterventionalStudyDesign.objectives: CT row 580 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.population | - | - | - | - | InterventionalStudyDesign.population: CT row 581 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.scheduleTimelines | - | - | - | - | InterventionalStudyDesign.scheduleTimelines: CT row 584 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.studyCells | - | - | - | - | InterventionalStudyDesign.studyCells: CT row 576 (Relationship, None) has no C-code in YAML |
| InterventionalStudyDesign.studyInterventions | - | - | - | - | InterventionalStudyDesign.studyInterventions: CT row 578 (Relationship, None) missing from YAML |
| MedicalDevice.embeddedProduct | - | - | - | - | MedicalDevice.embeddedProduct: CT row 547 (Relationship, None) missing from YAML |
| MedicalDevice.identifiers | - | - | - | - | MedicalDevice.identifiers: CT row 549 (Relationship, None) has no C-code in YAML |
| MedicalDeviceIdentifier.scope | - | - | - | - | MedicalDeviceIdentifier.scope: CT row 554 (Relationship, None) missing from YAML |
| NarrativeContent.children | - | - | - | - | NarrativeContent.children: CT row 279 (Relationship, None) missing from YAML |
| NarrativeContent.contentItem | - | - | - | - | NarrativeContent.contentItem: CT row 282 (Relationship, None) missing from YAML |
| NarrativeContent.next | - | - | - | - | NarrativeContent.next: CT row 281 (Relationship, None) missing from YAML |
| NarrativeContent.previous | - | - | - | - | NarrativeContent.previous: CT row 280 (Relationship, None) missing from YAML |
| Objective.dictionary | - | - | - | - | Objective.dictionary: CT row 69 (Relationship, None) missing from YAML |
| Objective.endpoints | - | - | - | - | Objective.endpoints: CT row 68 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.activities | - | - | - | - | ObservationalStudyDesign.activities: CT row 612 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.arms | - | - | - | - | ObservationalStudyDesign.arms: CT row 615 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.biospecimenRetentions | - | - | - | - | ObservationalStudyDesign.biospecimenRetentions: CT row 618 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.documentVersions | - | - | - | - | ObservationalStudyDesign.documentVersions: CT row 617 (Relationship, None) missing from YAML |
| ObservationalStudyDesign.elements | - | - | - | - | ObservationalStudyDesign.elements: CT row 616 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.eligibilityCriteria | - | - | - | - | ObservationalStudyDesign.eligibilityCriteria: CT row 619 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.encounters | - | - | - | - | ObservationalStudyDesign.encounters: CT row 611 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.epochs | - | - | - | - | ObservationalStudyDesign.epochs: CT row 614 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.estimands | - | - | - | - | ObservationalStudyDesign.estimands: CT row 608 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.indications | - | - | - | - | ObservationalStudyDesign.indications: CT row 606 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.objectives | - | - | - | - | ObservationalStudyDesign.objectives: CT row 609 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.population | - | - | - | - | ObservationalStudyDesign.population: CT row 610 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.scheduleTimelines | - | - | - | - | ObservationalStudyDesign.scheduleTimelines: CT row 613 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.studyCells | - | - | - | - | ObservationalStudyDesign.studyCells: CT row 605 (Relationship, None) has no C-code in YAML |
| ObservationalStudyDesign.studyInterventions | - | - | - | - | ObservationalStudyDesign.studyInterventions: CT row 607 (Relationship, None) missing from YAML |
| Organization.legalAddress | - | - | - | - | Organization.legalAddress: CT row 16 (Relationship, None) has no C-code in YAML |
| Organization.managedSites | - | - | - | - | Organization.managedSites: CT row 17 (Relationship, None) has no C-code in YAML |
| PopulationDefinition.criteria | - | - | - | - | PopulationDefinition.criteria: CT row 407 (Relationship, None) missing from YAML |
| Procedure.studyIntervention | - | - | - | - | Procedure.studyIntervention: CT row 146 (Relationship, None) missing from YAML |
| ProductOrganizationRole.appliesTo | - | - | - | - | ProductOrganizationRole.appliesTo: CT row 560 (Relationship, None) missing from YAML |
| ProductOrganizationRole.organization | - | - | - | - | ProductOrganizationRole.organization: CT row 561 (Relationship, None) missing from YAML |
| ReferenceIdentifier.scope | - | - | - | - | ReferenceIdentifier.scope: CT row 468 (Relationship, None) missing from YAML |
| ScheduleTimeline.entry | - | - | - | - | ScheduleTimeline.entry: CT row 256 (Relationship, None) missing from YAML |
| ScheduleTimeline.exits | - | - | - | - | ScheduleTimeline.exits: CT row 257 (Relationship, None) has no C-code in YAML |
| ScheduleTimeline.instances | - | - | - | - | ScheduleTimeline.instances: CT row 255 (Relationship, None) has no C-code in YAML |
| ScheduleTimeline.timings | - | - | - | - | ScheduleTimeline.timings: CT row 258 (Relationship, None) has no C-code in YAML |
| ScheduledActivityInstance.activities | - | - | - | - | ScheduledActivityInstance.activities: CT row 229 (Relationship, None) missing from YAML |
| ScheduledActivityInstance.defaultCondition | - | - | - | - | ScheduledActivityInstance.defaultCondition: CT row 233 (Relationship, None) missing from YAML |
| ScheduledActivityInstance.encounter | - | - | - | - | ScheduledActivityInstance.encounter: CT row 230 (Relationship, None) missing from YAML |
| ScheduledActivityInstance.epoch | - | - | - | - | ScheduledActivityInstance.epoch: CT row 234 (Relationship, None) missing from YAML |
| ScheduledActivityInstance.timeline | - | - | - | - | ScheduledActivityInstance.timeline: CT row 232 (Relationship, None) missing from YAML |
| ScheduledActivityInstance.timelineExit | - | - | - | - | ScheduledActivityInstance.timelineExit: CT row 231 (Relationship, None) missing from YAML |
| ScheduledDecisionInstance.conditionAssignments | - | - | - | - | ScheduledDecisionInstance.conditionAssignments: CT row 241 (Relationship, None) has no C-code in YAML |
| ScheduledDecisionInstance.defaultCondition | - | - | - | - | ScheduledDecisionInstance.defaultCondition: CT row 239 (Relationship, None) missing from YAML |
| ScheduledDecisionInstance.epoch | - | - | - | - | ScheduledDecisionInstance.epoch: CT row 240 (Relationship, None) missing from YAML |
| ScheduledInstance.defaultCondition | - | - | - | - | ScheduledInstance.defaultCondition: CT row 246 (Relationship, None) missing from YAML |
| ScheduledInstance.epoch | - | - | - | - | ScheduledInstance.epoch: CT row 247 (Relationship, None) missing from YAML |
| Study.documentedBy | - | - | - | - | Study.documentedBy: CT row 5 (Relationship, None) has no C-code in YAML |
| Study.versions | - | - | - | - | Study.versions: CT row 6 (Relationship, None) has no C-code in YAML |
| StudyAmendment.changes | - | - | - | - | StudyAmendment.changes: CT row 328 (Relationship, None) has no C-code in YAML |
| StudyAmendment.dateValues | - | - | - | - | StudyAmendment.dateValues: CT row 326 (Relationship, None) has no C-code in YAML |
| StudyAmendment.enrollments | - | - | - | - | StudyAmendment.enrollments: CT row 322 (Relationship, None) has no C-code in YAML |
| StudyAmendment.geographicScopes | - | - | - | - | StudyAmendment.geographicScopes: CT row 327 (Relationship, None) has no C-code in YAML |
| StudyAmendment.impacts | - | - | - | - | StudyAmendment.impacts: CT row 329 (Relationship, None) has no C-code in YAML |
| StudyAmendment.previous | - | - | - | - | StudyAmendment.previous: CT row 321 (Relationship, None) missing from YAML |
| StudyAmendment.primaryReason | - | - | - | - | StudyAmendment.primaryReason: CT row 323 (Relationship, None) has no C-code in YAML |
| StudyAmendment.secondaryReasons | - | - | - | - | StudyAmendment.secondaryReasons: CT row 324 (Relationship, None) has no C-code in YAML |
| StudyArm.populations | - | - | - | - | StudyArm.populations: CT row 91 (Relationship, None) missing from YAML |
| StudyCell.arm | - | - | - | - | StudyCell.arm: CT row 81 (Relationship, None) missing from YAML |
| StudyCell.elements | - | - | - | - | StudyCell.elements: CT row 83 (Relationship, None) missing from YAML |
| StudyCell.epoch | - | - | - | - | StudyCell.epoch: CT row 82 (Relationship, None) missing from YAML |
| StudyChange.changedSections | - | - | - | - | StudyChange.changedSections: CT row 531 (Relationship, None) has no C-code in YAML |
| StudyCohort.characteristics | - | - | - | - | StudyCohort.characteristics: CT row 389 (Relationship, None) has no C-code in YAML |
| StudyCohort.criteria | - | - | - | - | StudyCohort.criteria: CT row 388 (Relationship, None) missing from YAML |
| StudyCohort.indications | - | - | - | - | StudyCohort.indications: CT row 390 (Relationship, None) missing from YAML |
| StudyDefinitionDocument.children | - | - | - | - | StudyDefinitionDocument.children: CT row 454 (Relationship, None) missing from YAML |
| StudyDefinitionDocument.versions | - | - | - | - | StudyDefinitionDocument.versions: CT row 453 (Relationship, None) has no C-code in YAML |
| StudyDefinitionDocumentVersion.contents | - | - | - | - | StudyDefinitionDocumentVersion.contents: CT row 459 (Relationship, None) has no C-code in YAML |
| StudyDefinitionDocumentVersion.dateValues | - | - | - | - | StudyDefinitionDocumentVersion.dateValues: CT row 460 (Relationship, None) has no C-code in YAML |
| StudyDesign.activities | - | - | - | - | StudyDesign.activities: CT row 31 (Relationship, None) has no C-code in YAML |
| StudyDesign.arms | - | - | - | - | StudyDesign.arms: CT row 28 (Relationship, None) has no C-code in YAML |
| StudyDesign.biospecimenRetentions | - | - | - | - | StudyDesign.biospecimenRetentions: CT row 32 (Relationship, None) has no C-code in YAML |
| StudyDesign.documentVersions | - | - | - | - | StudyDesign.documentVersions: CT row 30 (Relationship, None) missing from YAML |
| StudyDesign.elements | - | - | - | - | StudyDesign.elements: CT row 29 (Relationship, None) has no C-code in YAML |
| StudyDesign.eligibilityCriteria | - | - | - | - | StudyDesign.eligibilityCriteria: CT row 33 (Relationship, None) has no C-code in YAML |
| StudyDesign.encounters | - | - | - | - | StudyDesign.encounters: CT row 25 (Relationship, None) has no C-code in YAML |
| StudyDesign.epochs | - | - | - | - | StudyDesign.epochs: CT row 27 (Relationship, None) has no C-code in YAML |
| StudyDesign.estimands | - | - | - | - | StudyDesign.estimands: CT row 22 (Relationship, None) has no C-code in YAML |
| StudyDesign.indications | - | - | - | - | StudyDesign.indications: CT row 20 (Relationship, None) has no C-code in YAML |
| StudyDesign.objectives | - | - | - | - | StudyDesign.objectives: CT row 23 (Relationship, None) has no C-code in YAML |
| StudyDesign.population | - | - | - | - | StudyDesign.population: CT row 24 (Relationship, None) has no C-code in YAML |
| StudyDesign.scheduleTimelines | - | - | - | - | StudyDesign.scheduleTimelines: CT row 26 (Relationship, None) has no C-code in YAML |
| StudyDesign.studyCells | - | - | - | - | StudyDesign.studyCells: CT row 19 (Relationship, None) has no C-code in YAML |
| StudyDesign.studyInterventions | - | - | - | - | StudyDesign.studyInterventions: CT row 21 (Relationship, None) missing from YAML |
| StudyDesignPopulation.cohorts | - | - | - | - | StudyDesignPopulation.cohorts: CT row 60 (Relationship, None) has no C-code in YAML |
| StudyDesignPopulation.criteria | - | - | - | - | StudyDesignPopulation.criteria: CT row 61 (Relationship, None) missing from YAML |
| StudyElement.studyInterventions | - | - | - | - | StudyElement.studyInterventions: CT row 104 (Relationship, None) missing from YAML |
| StudyElement.transitionEndRule | - | - | - | - | StudyElement.transitionEndRule: CT row 103 (Relationship, None) has no C-code in YAML |
| StudyElement.transitionStartRule | - | - | - | - | StudyElement.transitionStartRule: CT row 102 (Relationship, None) has no C-code in YAML |
| StudyEpoch.next | - | - | - | - | StudyEpoch.next: CT row 99 (Relationship, None) missing from YAML |
| StudyEpoch.previous | - | - | - | - | StudyEpoch.previous: CT row 98 (Relationship, None) missing from YAML |
| StudyIdentifier.scope | - | - | - | - | StudyIdentifier.scope: CT row 9 (Relationship, None) missing from YAML |
| StudyIntervention.administrations | - | - | - | - | StudyIntervention.administrations: CT row 362 (Relationship, None) has no C-code in YAML |
| StudyRole.appliesTo | - | - | - | - | StudyRole.appliesTo: CT row 522 (Relationship, None) missing from YAML |
| StudyRole.assignedPersons | - | - | - | - | StudyRole.assignedPersons: CT row 520 (Relationship, None) has no C-code in YAML |
| StudyRole.masking | - | - | - | - | StudyRole.masking: CT row 521 (Relationship, None) has no C-code in YAML |
| StudyRole.organizations | - | - | - | - | StudyRole.organizations: CT row 523 (Relationship, None) missing from YAML |
| StudyVersion.abbreviations | - | - | - | - | StudyVersion.abbreviations: CT row 341 (Relationship, None) has no C-code in YAML |
| StudyVersion.amendments | - | - | - | - | StudyVersion.amendments: CT row 335 (Relationship, None) has no C-code in YAML |
| StudyVersion.dateValues | - | - | - | - | StudyVersion.dateValues: CT row 334 (Relationship, None) has no C-code in YAML |
| StudyVersion.documentVersions | - | - | - | - | StudyVersion.documentVersions: CT row 336 (Relationship, None) missing from YAML |
| StudyVersion.referenceIdentifiers | - | - | - | - | StudyVersion.referenceIdentifiers: CT row 342 (Relationship, None) has no C-code in YAML |
| StudyVersion.studyDesigns | - | - | - | - | StudyVersion.studyDesigns: CT row 338 (Relationship, None) has no C-code in YAML |
| StudyVersion.studyIdentifiers | - | - | - | - | StudyVersion.studyIdentifiers: CT row 337 (Relationship, None) has no C-code in YAML |
| StudyVersion.titles | - | - | - | - | StudyVersion.titles: CT row 339 (Relationship, None) has no C-code in YAML |
| SubjectEnrollment.forGeographicScope | - | - | - | - | SubjectEnrollment.forGeographicScope: CT row 352 (Relationship, None) has no C-code in YAML |
| SubjectEnrollment.forStudyCohort | - | - | - | - | SubjectEnrollment.forStudyCohort: CT row 353 (Relationship, None) missing from YAML |
| SubjectEnrollment.forStudySite | - | - | - | - | SubjectEnrollment.forStudySite: CT row 351 (Relationship, None) missing from YAML |
| Substance.referenceSubstance | - | - | - | - | Substance.referenceSubstance: CT row 498 (Relationship, None) has no C-code in YAML |
| Substance.strengths | - | - | - | - | Substance.strengths: CT row 497 (Relationship, None) has no C-code in YAML |
| SyntaxTemplate.dictionary | - | - | - | - | SyntaxTemplate.dictionary: CT row 288 (Relationship, None) missing from YAML |
| SyntaxTemplateDictionary.parameterMaps | - | - | - | - | SyntaxTemplateDictionary.parameterMaps: CT row 294 (Relationship, None) has no C-code in YAML |
| Timing.relativeFromScheduledInstance | - | - | - | - | Timing.relativeFromScheduledInstance: CT row 271 (Relationship, None) missing from YAML |
| Timing.relativeToScheduledInstance | - | - | - | - | Timing.relativeToScheduledInstance: CT row 272 (Relationship, None) missing from YAML |

## Classification-style definitions without a value list (`CLASSIFICATION_WITHOUT_VALUE_LIST`, 1)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| Procedure.procedureType | - | C188848 | - | A characterization or classification of the study procedure. | Procedure.procedureType: definition starts with 'A characterization or classification of' but Has Value List = N (CT row 141) |

## Value list vs. YAML type inconsistencies (`VALUE_LIST_TYPE_MISMATCH`, 7)

| Location | YAML C-code | CT C-code | YAML value | CT value | Detail |
| --- | --- | --- | --- | --- | --- |
| AliasCode.standardCode | C215528 | C215528 | #/Code | N | AliasCode.standardCode: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| AliasCode.standardCodeAliases | C215529 | C215529 | #/Code | N | AliasCode.standardCodeAliases: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| BiomedicalConcept.code | C207469 | C207469 | #/AliasCode | N | BiomedicalConcept.code: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| BiomedicalConceptCategory.code | C201315 | C201315 | #/AliasCode | N | BiomedicalConceptCategory.code: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| BiomedicalConceptProperty.code | C201318 | C201318 | #/AliasCode | N | BiomedicalConceptProperty.code: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| CommentAnnotation.codes | C215556 | C215556 | #/Code | N | CommentAnnotation.codes: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
| ResponseCode.code | C217013 | C217013 | #/Code | N | ResponseCode.code: YAML attribute is Code-typed but CT declares no value list (Has Value List = N) |
