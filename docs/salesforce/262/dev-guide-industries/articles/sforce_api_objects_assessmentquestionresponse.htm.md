---
page_id: sforce_api_objects_assessmentquestionresponse.htm
title: AssessmentQuestionResponse
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentquestionresponse.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentQuestionResponse

Stores the responses submitted to an assessment. This object is
available in API version 55.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`search()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssessmentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  Required. The ID of the assessment associated with this record.  This is a relationship field.  Relationship Name  Assessment  Relationship Type  Master-detail  Refers To  Assessment (the master object) |
| AssessmentQuestionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the assessment question associated with this record.  This is a relationship field.  Relationship Name  AssessmentQuestion  Relationship Type  Lookup  Refers To  AssessmentQuestionVersion |
| ChoiceValue | Type  textarea  Properties  Create, Filter, Nillable, Sort, Update  Description  The response value when the question's data type is choice. |
| CurrencyValue | Type  currency  Properties  Create, Filter, Nillable, Sort, Update  Description  The response value when the question's data type is currency. |
| DateTimeValue | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The response value when the question's data type is date time. |
| DateValue | Type  date  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The response value when the question's data type is date. |
| DecimalResponseValue | Type  double  Properties  Create, Filter, idLookup, Nillable, Sort, Update  Description  The response value when the question's data type is decimal. |
| ExtlAssessmentQuestionText | Type  textarea  Properties  Create, Nillable, Update  Description  Stores the external assessment question text. |
| ExtlResponseValueIdentifier | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The unique identifier of a response to a question in an external assessment. |
| IntegerResponseValue | Type  int  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  The response value when the associated assessment question's data type is integer. |
| IsTrueOrFalseValue | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The response value when the question's data type is boolean.  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  Required. The name of this record. |
| OriginType | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the origin of the assessment question response.  Possible values are:  - `Auto` - `Manual` - `Override` |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| ParentAsmtQuestionVersionId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The ID of the related assessment question version associated with the assessment question response.  This is a relationship field.  Relationship Name  ParentAsmtQuestionVersion  Relationship Type  Lookup  Refers To  AssessmentQuestionVersion |
| RespondentTimezone | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The auto-generated timezone of the respondent submitting the assessment response. |
| ResponseText | Type  textarea  Properties  Create, Nillable, Update  Description  The response value when the question's data type is text. |
| ResponseType | Type  string  Properties  Filter, Group, Nillable, Sort  Description  The data type of the response value submitted. |
| ResponseValue | Type  textarea  Properties  Nillable  Description  The response value to the assessment question. |
| ResponseValueScore | Type  double  Properties  Create, Filter, Nillable, Sort, Update  Description  The score of the assessment question response value. |
| ReviewerId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The person who reviewed and edited the response.  This field is a polymorphic relationship field.  Relationship Name  Reviewer  Refers To  Account, Contact, HealthcareProvider, User |
| ReviewerRoleId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The role of the person who reviewed and edited the response.  This field is a polymorphic relationship field.  Relationship Name  ReviewerRole  Refers To  CodeSet, CodeSetBundle |
| TimeValue | Type  time  Properties  Create, Filter, idLookup, Nillable, Sort, Update  Description  The response value when the question's data type is time. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentQuestionResponseChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentQuestionResponseFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentQuestionResponseHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssessmentQuestionResponseShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
