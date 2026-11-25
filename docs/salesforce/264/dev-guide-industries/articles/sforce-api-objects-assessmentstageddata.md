---
page_id: sforce-api-objects-assessmentstageddata
title: AssessmentStagedData
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentstageddata.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Discovery Framework
parent_page: discovery-framework-standard-objects
legacy_page_id: sforce_api_objects_assessmentstageddata.htm
fetched_at: 2026-11-25
---

# AssessmentStagedData

Represents the responses to assessment questions when a user captures and submits information with the Discovery Framework Data Capture Flow on a mobile device. The information is used to create assessment and related records. This object is available in API version 63.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### DynamicDataCaptureId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The Dynamic Data Capture associated with the assessment staged data.

This field is a relationship field.

- 

**Relationship Name**: DynamicDataCapture

- 

**Refers To**: DynamicDataCapture

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Auto-assigned number that identifies the assessment staged data record.

### OwnerId

- 

**Type**: reference

- 

**Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- 

**Description**: The ID of the user who owns the record.

This field is a polymorphic relationship field.

- 

**Relationship Name**: Owner

- 

**Refers To**: Group, User

### ParentId

- 

**Type**: reference

- 

**Properties**: Create, Filter, Group, Nillable, Sort, Update

- 

**Description**: The parent associated with the assessment staged data record.

This field is a relationship field.

- 

**Relationship Name**: Parent

- 

**Refers To**: AssessmentStagedData

### Response

- **Type**: textarea

- **Properties**: Create, Nillable, Update

- **Description**: The response to assessment questions as submitted by users, in JSON format.

### ResponseProcessingError

- **Type**: textarea

- **Properties**: Filter, Nillable, Sort

- **Description**: The error encountered while processing the question responses for creating assessment and related records.

### ResponseProcessingStatus

- 

**Type**: picklist

- 

**Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- 

**Description**: Specifies the status of the processing of question responses, and the creation of the assessment and its related records.

- 

**Default value**: `Pending`

- 

**Possible values**:

  - `Completed`

  - `Failed`

  - `Pending`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AssessmentStagedDataChangeEvent](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-change-event.html)**

: 

Change events are available for the object.

**[AssessmentStagedDataFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[AssessmentStagedDataHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

**[AssessmentStagedDataOwnerSharingRule](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-ownersharingrule.html)**

: 

Sharing rules are available for the object.

**[AssessmentStagedDataShare](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-share.html)**

: 

Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-assessmentstageddata.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
