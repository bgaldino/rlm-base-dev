---
page_id: discovery_framework_standard_objects.htm
title: Discovery Framework Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discovery_framework_standard_objects.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Discovery Framework Standard Objects

This section lists the standard objects associated with Discovery Framework with their
  standard fields. Use the standard objects to create assessment questions and forms.

| Available in: Discovery Framework is available in Lightning Experience and included in Financial Services Cloud, Health Cloud, Public Sector Solutions, and Consumer Goods Cloud. |
| --- |

  

- 
**[Assessment](./sforce-api-objects-assessment.md)**  

Stores the header data for an assessment. This object is       available in API version 55.0 and later.

- 
**[AssessmentDefinition](./sforce-api-objects-assessmentdefinition.md)**  

       Represents the definition of an assessment including details such as the last          revised date and purpose. This object is available in API version 63.0 and later. 

- 
**[AssessmentQuestion](./sforce-api-objects-assessmentquestion.md)**  

Stores the questions required for an assessment. This object is       available in API version 55.0 and later.

- 
**[AssessmentQuestionAssignment](./sforce-api-objects-assessmentquestionassignment.md)**  

Represents a junction between an assessment question set and an          assessment question. This object is available in API version 55.0 and       later.

- 
**[AssessmentQuestionResponse](./sforce-api-objects-assessmentquestionresponse.md)**  

Stores the responses submitted to an assessment. This object is       available in API version 55.0 and later.

- 
**[AssessmentQuestionSet](./sforce-api-objects-assessmentquestionset.md)**  

Container object for assessment questions. This object is       available in API version 55.0 and later.

- 
**[AssessmentQuestionVersion](./sforce-api-objects-assessmentquestionversion.md)**  

Stores the question versions for the assessment questions. This       object is available in API version 55.0 and later.

- 
**[AssessmentQstnVerChoice2](./sforce-api-objects-assessmentqstnverchoice2.md)**  

       Represents a choice a user can select for an assessment question          version. This object is available in API version 63.0 and later. 

- 
**[AssessmentReason](./sforce-api-objects-assessmentreason.md)**  

       Represents the reasons for an assessment such as the associated coverage          information. This object is available in API version 63.0 and later. 

- 
**[AssessmentSavedSession](./sforce-api-objects-assessmentsavedsession.md)**  

       Represents a session of an assessment that's saved to resume for later.       This object is available in API version 62.0 and later.

- 
**[AssessmentSignature](./sforce-api-objects-assessmentsignature.md)**  

       Stores the respondent’s signature during an assessment. This object is       available in API version 57.0 and later. 

- 
**[AssessmentStagedData](./sforce-api-objects-assessmentstageddata.md)**  

       Represents the responses to assessment questions when a user captures and          submits information with the Discovery Framework Data Capture Flow on a mobile device. The          information is used to create assessment and related records. This object is available       in API version 63.0 and later. 

- 
**[DocumentDecisionRequirement](./sforce-api-objects-documentdecisionrequirement.md)**  

       Represents the decision criteria that will be used to determine applicable          documents. This object is available in API version 59.0 and later. 

- 
**[ExternalAssessmentDefinition](./sforce-api-objects-externalassessmentdefinition.md)**  

       Stores information about external assessments. This object is available       in API version 60.0 and later. 

- 
**[OmniProcessAsmtQuestionVer](./sforce-api-objects-omniprocessasmtquestionver.md)**  

Represents a junction between an OmniScript process and an assessment          question version. This object is available in API version 55.0 and later.

- 
**[SuggestedAssessmentDef](./sforce-api-objects-suggestedassessmentdef.md)**  

       Stores information about suggested assessments. This object is available       in API version 60.0 and later.

- 
**[SuggestedAssessmentReason](./sforce-api-objects-suggestedassessmentreason.md)**  

       Stores the reasons for a suggested assessment. This object is available       in API version 60.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/discovery_framework_standard_objects.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
