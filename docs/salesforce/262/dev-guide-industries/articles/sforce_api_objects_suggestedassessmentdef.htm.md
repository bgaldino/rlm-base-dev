---
page_id: sforce_api_objects_suggestedassessmentdef.htm
title: SuggestedAssessmentDef
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_suggestedassessmentdef.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# SuggestedAssessmentDef

Stores information about suggested assessments. This object is available
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
| AssessmentDefinitionRefId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The reference record of the object associated with the suggested assessment.  This field is a polymorphic relationship field.  Relationship Name  AssessmentDefinitionRef  Relationship Type  Lookup  Refers To  ExternalAssessmentDefinition, OmniProcess |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user viewed this record. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| PartyId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The party for whom the assessment is suggested.  This field is a polymorphic relationship field.  Relationship Name  Party  Relationship Type  Lookup  Refers To  Account |
| SourceContextId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The context from which the suggested assessment definition record was created.  This field is a polymorphic relationship field.  Relationship Name  SourceContext  Relationship Type  Lookup  Refers To  Case, ClinicalServiceRequest |
| Status | Type  picklist  Properties  Create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the status of the suggested assessment.  Possible values are:  - `Completed` - `Ignored` - `InProgress`—In Progress - `Suggested` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[SuggestedAssessmentDefFeed](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[SuggestedAssessmentDefHistory](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.

[SuggestedAssessmentDefShare](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
