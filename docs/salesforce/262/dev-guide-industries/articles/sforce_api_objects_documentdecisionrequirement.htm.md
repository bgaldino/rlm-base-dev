---
page_id: sforce_api_objects_documentdecisionrequirement.htm
title: DocumentDecisionRequirement
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_documentdecisionrequirement.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# DocumentDecisionRequirement

Represents the decision criteria that will be used to determine applicable
documents. This object is available in API version 59.0 and later.

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
| Context | Type  string  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The context that's used to determine the applicable documents to be uploaded. |
| DocumentReferenceObjectId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  The document category or the document type related to the document decision.  This field is a polymorphic relationship field.  Relationship Name  DocumentReferenceObject  Relationship Type  Lookup  Refers To  DocumentCategory, DocumentType |
| HelpText | Type  string  Properties  Create, Filter, Nillable, Sort, Update  Description  The help information to show to memebers when uploading the document. |
| IsUploadRequired | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether a document upload for a document category is required (true) or not (false).  The default value is `false`. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Create, Filter, Group, idLookup, Sort, Update  Description  The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[DocumentDecisionRequirementChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[DocumentDecisionRequirementFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[DocumentDecisionRequirementHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[DocumentDecisionRequirementOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm "HTML (New Window)")
:   Sharing rules are available for the object.

[DocumentDecisionRequirementShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
