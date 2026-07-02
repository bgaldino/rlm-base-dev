---
page_id: sforce_api_objects_assessmentqstnverchoice2.htm
title: AssessmentQstnVerChoice2
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentqstnverchoice2.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentQstnVerChoice2

Represents a choice a user can select for an assessment question
version. This object is available in API version 63.0 and later.

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

## Supported Calls

Only users with the Education Cloud Full Access
permission set can access this object.

## Fields

| Field | Details |
| --- | --- |
| AssessmentQuestionVersionId | Type  reference  Properties  Create, Filter, Group, Sort  Description  The assessment question version related to the assessment question version choice.  This field is a relationship field.  Relationship Name  AssessmentQuestionVersion  Relationship Type  Master-detail  Refers To  AssessmentQuestionVersion (the master object) |
| CurrencyIsoCode | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The ISO code for the currency related to the assessment question version choice.  Possible values are:  - `GBP`—British Pound - `USD`—U.S. Dollar  The default value is `USD`. |
| DisplayOrder | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The order in which the question choices is displayed for an assessment question version. |
| Icon | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The name of the icon presented as a question choice when the assessment question is of the icon type. |
| Key | Type  string  Properties  Create, Filter, Group, Sort, Update  Description  A unique code or identifier for a question choice that's mapped to an assessment question version. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last accessed this record, a record related to this record, or a list view. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp when the current user last viewed this record or list view. If this value is null, the user might have only accessed this record or list view (LastReferencedDate) but not viewed it. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the assessment question version choice. |
| UniqueIndex | Type  string  Properties  Filter, Group, idLookup, Nillable, Sort  Description  The unique index for the AssessmentQuestionVersionId and Key pair.  This field is a calculated field. |
