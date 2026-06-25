---
page_id: sforce_api_objects_suggestedassessmentreason.htm
title: SuggestedAssessmentReason
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_suggestedassessmentreason.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# SuggestedAssessmentReason

Stores the reasons for a suggested assessment. This object is available
in API version 60.0 and later.

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
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user viewed this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the record. |
| PrimaryAsmtQuestionResponseId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The response value in the primary assessment that triggered the suggested assessment.  This field is a relationship field.  Relationship Name  PrimaryAsmtQuestionResponse  Relationship Type  Lookup  Refers To  AssessmentQuestionResponse |
| PrimaryAssessmentId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The primary assessment from which a suggested assessment was triggered.  This field is a relationship field.  Relationship Name  PrimaryAssessment  Relationship Type  Lookup  Refers To  Assessment |
| SuggestedAssessmentDefId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The suggested assessment associated with the suggested assessment reason.  This field is a relationship field.  Relationship Name  SuggestedAssessmentDef  Relationship Type  Lookup  Refers To  SuggestedAssessmentDef |
| SuggestionSourceType | Type  picklist  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  Specifies the source of the logic by which an assessment was suggested.  Possible values are:  - `Business Rule` - `MCG` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[SuggestedAssessmentReasonFeed](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[b](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.
