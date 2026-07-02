---
page_id: sforce_api_objects_externalassessmentdefinition.htm
title: ExternalAssessmentDefinition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_externalassessmentdefinition.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# ExternalAssessmentDefinition

Stores information about external assessments. This object is available
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
| AssessmentCategory | Type  picklist  Properties  Create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  Specifies the guideline category the external assessment belongs to.  Possible values are:  - `CCG` - `TC` |
| AssessmentContentVersion | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The version number of the external assessment's content. |
| CustomAssessmentDisclaimer | Type  textarea  Properties  Create, Nillable, Update  Description  A disclaimer for custom assessments sent by the external API. |
| ExternalIdentifier | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The unique identifier of the external assessment. |
| IsCustomAssessment | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the external assessment is a custom assessment authored by the user (true) or an out-of-the-box assessment (false).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user referenced this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The most recent date on which a user viewed this record. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| SourceSystemName | Type  picklist  Properties  Create, Filter, Group, Sort, Update  Description  The source system from which the record was retrieved.  Possible values are:  - `MCG` |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[ExternalAssessmentDefinitionFeed](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[ExternalAssessmentDefinitionHistory](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.

[ExternalAssessmentDefinitionShare](https://developer.salesforce.com/docs/atlas.en-us.248.0.object_reference.meta/object_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
