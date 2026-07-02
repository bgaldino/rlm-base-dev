---
page_id: sforce_api_objects_assessmentstageddata.htm
title: AssessmentStagedData
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_objects_assessmentstageddata.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: discovery_framework_standard_objects.htm
fetched_at: 2026-06-25
---

# AssessmentStagedData

Represents the responses to assessment questions when a user captures and
submits information with the Discovery Framework Data Capture Flow on a mobile device. The
information is used to create assessment and related records. This object is available
in API version 63.0 and later.

## Supported Calls

`create()`,
`delete()`,
`describeLayout()`,
`describeSObjects()`,
`getDeleted()`,
`getUpdated()`,
`query()`,
`retrieve()`,
`undelete()`,
`update()`,
`upsert()`

## Fields

| Field | Details |
| --- | --- |
| DynamicDataCaptureId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The Dynamic Data Capture associated with the assessment staged data.  This field is a relationship field.  Relationship Name  DynamicDataCapture  Refers To  DynamicDataCapture |
| Name | Type  string  Properties  Autonumber, Defaulted on create, Filter, idLookup, Sort  Description  Auto-assigned number that identifies the assessment staged data record. |
| OwnerId | Type  reference  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  The ID of the user who owns the record.  This field is a polymorphic relationship field.  Relationship Name  Owner  Refers To  Group, User |
| ParentId | Type  reference  Properties  Create, Filter, Group, Nillable, Sort, Update  Description  The parent associated with the assessment staged data record.  This field is a relationship field.  Relationship Name  Parent  Refers To  AssessmentStagedData |
| Response | Type  textarea  Properties  Create, Nillable, Update  Description  The response to assessment questions as submitted by users, in JSON format. |
| ResponseProcessingError | Type  textarea  Properties  Filter, Nillable, Sort  Description  The error encountered while processing the question responses for creating assessment and related records. |
| ResponseProcessingStatus | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update  Description  Specifies the status of the processing of question responses, and the creation of the assessment and its related records.  Possible values are:  - `Completed` - `Failed` - `Pending`  The default value is `Pending`. |

## Associated Objects

This object has the following associated objects. If the API version isn’t specified,
they’re available in the same API versions as this object. Otherwise, they’re available
in the specified API version and later.

[AssessmentStagedDataChangeEvent](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_change_event.htm)
:   Change events are available for the object.

[AssessmentStagedDataFeed](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_feed.htm)
:   Feed tracking is available for the object.

[AssessmentStagedDataHistory](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_history.htm)
:   History is available for tracked fields of the object.

[AssessmentStagedDataOwnerSharingRule](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_ownersharingrule.htm)
:   Sharing rules are available for the object.

[AssessmentStagedDataShare](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/sforce_api_associated_objects_share.htm)
:   Sharing is available for the object.
