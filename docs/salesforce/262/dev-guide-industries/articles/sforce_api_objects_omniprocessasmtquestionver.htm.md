---
page_id: sforce_api_objects_omniprocessasmtquestionver.htm
title: OmniProcessAsmtQuestionVer
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_omniprocessasmtquestionver.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# OmniProcessAsmtQuestionVer

Represents a junction between an OmniScript process and an assessment
question version. This object is available in API version 55.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

| Field | Details |
| --- | --- |
| AssessmentQuestionVersionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of assessment question version associated with the Omni Process assessment question version record.  This is a relationship field.  Relationship Name  AssessmentQuestionVersion  Relationship Type  Lookup  Refers To  AssessmentQuestionVersion |
| IsImportant | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the assessment question version is important (`true`) or not (`false`).  The default value is `false`.  Available in API version 59.0 and later. |
| IsPrefill | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the assessment question version is prefilled (`true`) or not (`false`).  The default value is `false`.  Available in API version 60.0 and later. |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the Omni Process assessment question version record. |
| OmniProcessElementId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the Omni Process element associated with the Omni Process assessment question version record.  This is a relationship field.  Relationship Name  OmniProcessElement  Relationship Type  Lookup  Refers To  OmniProcessElement |
| OmniProcessId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the Omni Process associated with the Omni Process assessment question version record.  This is a relationship field.  Relationship Name  OmniProcess  Relationship Type  Lookup  Refers To  OmniProcess |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[OmniProcessAsmtQuestionVerChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[OmniProcessAsmtQuestionVerFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[OmniProcessAsmtQuestionVerHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[OmniProcessAsmtQuestionVerOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)
:   Sharing rules are available for the object.

[OmniProcessAsmtQuestionVerShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
