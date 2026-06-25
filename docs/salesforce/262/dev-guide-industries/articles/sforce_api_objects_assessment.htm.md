---
page_id: sforce_api_objects_assessment.htm
title: Assessment
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessment.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# Assessment

Stores the header data for an assessment. This object is
available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AccountId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the account for which the assessment was taken.  This is a relationship field.  Relationship Name  Account  Relationship Type  Lookup  Refers To  Account |
| ApplicantId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The applicant for whom the assessment was carried out. This field is available only if you have enabled Integrated Onboarding for Financial Services Cloud.  This field is a relationship field. |
| AssessmentRating | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The overall rating for the assessment.  Possible values are:  - `High` - `Low` - `Medium` |
| AssessmentStagedDataId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The Assessment Staged Data that's associated with this assessment.  This field is a relationship field.  Relationship Name  AssessmentStagedData  Refers To  AssessmentStagedData |
| AssessmentStatus | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Required. The status of the assessment.  Possible values are:  - `Canceled` - `Completed` - `In Progress` |
| AssessorId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The person who carried out the assessment and recorded the responses.  This field is a polymorphic relationship field.  Relationship Name  Assessor  Refers To  Account, Contact, HealthcareProvider, User |
| CareProgramSiteId | Type  reference  Properties  Filter, Group, Nillable, Sort  Description  Stores the derived Care Program Site Identifier when the site assessment is done in the context of care program sites. This field is available in API version 63.0 when Site Management is enabled.  This is a relationship field.  Relationship Name  CareProgramSite  Refers To  CareProgramSite |
| CaseId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the case associated with the assessment.  This is a relationship field.  Relationship Name  Case  Relationship Type  Lookup  Refers To  Case |
| CompletedDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date and time when the assessment was completed. |
| ContactId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the contact associated with the assessment.  This is a relationship field.  Relationship Name  Contact  Relationship Type  Lookup  Refers To  Contact |
| EffectiveDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The timestamp from when the assessment is effective. |
| ExpirationDateTime | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The timestamp from when the assessment lapses. |
| ExternalAssessmentDefId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The associated external assessment definition.  This field is a relationship field.  Relationship Name  ExternalAssessmentDef  Relationship Type  Lookup  Refers To  ExternalAssessmentDefinition |
| Identifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier of a completed or partially completed assessment in the source system. |
| IsSavedForLater | Type  boolean  Properties  Defaulted on create, Filter, Group, Sort  Description  Indicates whether the assessment is saved as a draft (true) or not (false). The default value is false. This field is available in API version 60.0 and later. |
| IsSuggestedAssessment | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the assessment is a suggested assessment (true) or not (false).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of the assessment. |
| OmniProcessId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The OmniScript associated with the assessment record. This field is available in API version 56.0 and later.  This field is a relationship field.  Relationship Name  OmniProcess  Relationship Type  Lookup  Refers To  OmniProcess |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ParentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the related assessment, if any.  This is a relationship field.  Relationship Name  Parent  Relationship Type  Lookup  Refers To  Assessment |
| PartyProfileId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Represents information about the profile of a party, such as a contact, account, or lead. This field is available only if you’ve enabled the Know Your Customer setting in your Salesforce org.  Relationship Name  PartyProfile  Relationship Type  Lookup  Refers To  PartyProfile |
| ResponseContextId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The record in which context the response was taken. This field is available in API version 56.0 and later where Public Sector Solutions is enabled.  This field is a polymorphic relationship field.  Relationship Name  ResponseContext  Relationship Type  Lookup  Refers To  - ApplicationFormEvaluation - Available in API version 62.0   and later - BusinessLicenseApplication - CarePlan - IndividualApplication - PublicComplaint - VettingEvaluation - Available in API version 62.0 and   later - Visit |
| Type | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the type of assessment. This field is available only if you have enabled Integrated Onboarding for Financial Services Cloud. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssessmentShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
