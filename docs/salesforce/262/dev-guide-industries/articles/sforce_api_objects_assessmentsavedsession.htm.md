---
page_id: sforce_api_objects_assessmentsavedsession.htm
title: AssessmentSavedSession
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentsavedsession.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentSavedSession

Represents a session of an assessment that's saved to resume for later.
This object is available in API version 62.0 and later.

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
| AssessmentId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The assessment record for which the session is saved.  This field is a relationship field.  Relationship Name  Assessment  Relationship Type  Master-detail  Refers To  Assessment |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user referenced the record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user viewed the record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the assessment saved session record. |
| UsageType | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the use case of the saved assessment session.  Possible values are:  - `HealthCloud` |
