---
page_id: sforce_api_objects_assessmentquestionassignment.htm
title: AssessmentQuestionAssignment
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentquestionassignment.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentQuestionAssignment

Represents a junction between an assessment question set and an
assessment question. This object is available in API version 55.0 and
later.

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
| AssessmentQuestionId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the assessment question associated with this record.  This is a relationship field.  Relationship Name  AssessmentQuestion  Relationship Type  Lookup  Refers To  AssessmentQuestion |
| AssessmentQuestionSetId | Type  reference  Properties  Create, Filter, Group, Sort, Update  Description  Required. The ID of the assessment question set associated with this record.  This is a relationship field.  Relationship Name  AssessmentQuestionSet  Relationship Type  Lookup  Refers To  AssessmentQuestionSet |
| LastReferencedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed a record related to this record. |
| LastViewedDate | Type  dateTime  Properties  Filter, Nillable, Sort  Description  The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Required. The name of the record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who created the relationship record.  This is a polymorphic relationship field.  Relationship Name  Owner  Relationship Type  Lookup  Refers To  Group, User |
| SequenceNumber | Type  int  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The sequence number for an assessment question in an assessment question set.  Available in API version 64.0 and later. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentQuestionAssignmentChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentQuestionAssignmentFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm "HTML (New Window)")
:   Feed tracking is available for the object.

[AssessmentQuestionAssignmentHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm "HTML (New Window)")
:   History is available for tracked fields of the object.

[AssessmentQuestionAssignmentShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm "HTML (New Window)")
:   Sharing is available for the object.
