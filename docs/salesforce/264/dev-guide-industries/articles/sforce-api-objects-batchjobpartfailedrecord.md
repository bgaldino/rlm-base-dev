---
page_id: sforce-api-objects-batchjobpartfailedrecord
title: BatchJobPartFailedRecord
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-batchjobpartfailedrecord.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Data Processing Engine, Batch Management, and Monitor Workflow Services
parent_page: monitor-workflow-services-dev-overview
legacy_page_id: sforce_api_objects_batchjobpartfailedrecord.htm
fetched_at: 2026-11-25
---

# BatchJobPartFailedRecord

Represents records that a batch job part couldn’t successfully process. This object is available in API version 51.0 and later.

## Supported Calls

`describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`

## Special Access Rules

To know the permissions needed to access this object, See [User Permissions for Data Processing Engine](https://help.salesforce.com/s/articleView?id=ind.dpe_setup.htm) or [User Permissions for Batch Management](https://help.salesforce.com/s/articleView?id=ind.concept_batch_management_editions.htm).

## Fields

### BatchJobId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Nillable, Sort

- 

**Description**: The unique identifier of the associated batch job.

This is a relationship field.

- 

**Relationship Name**: BatchJob

- 

**Relationship Type**: Lookup

- 

**Refers To**: BatchJob

### BatchJobPartId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Sort

- 

**Description**: The unique identifier of the associated batch job part.

This is a relationship field.

- 

**Relationship Name**: BatchJobPart

- 

**Relationship Type**: Lookup

- 

**Refers To**: BatchJobPart

### ErrorDescription

- **Type**: string

- **Properties**: Filter, Nillable, Sort

- **Description**: The error message that indicates why the batch job part couldn’t process the records.

### Name

- **Type**: string

- **Properties**: Filter, Group, idLookup, Sort

- **Description**: The name of the batch job part failed record.

### ProcessingGroupKey

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Length**: 100

- **Description**: The field used for creating batch job parts. It can be a Group By field selected from the UI or a Partition Key from the API.

### Record

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The unique identifier of the batch record that processed the failed records.

### RecordName

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The name of the record that’s associated with the batch job part failed record.

### ResubmittedBatchJobId

- 

**Type**: reference

- 

**Properties**: Filter, Group, Nillable, Sort

- 

**Description**: The batch job used to submit failed records. This field is available in API version 52.0 and later.

This is a relationship field.

- 

**Relationship Name**: ResubmittedBatchJob

- 

**Relationship Type**: Lookup

- 

**Refers To**: BatchJob

### Status

- 

**Type**: picklist

- 

**Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- 

**Description**: Specifies the status of the failed records. This field is available in API version 52.0 and later.

- 

**Default value**: `Failed`

- 

**Possible values**:

  - `Failed`

  - `Resubmitted`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[BatchJobPartFailedRecordFeed](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-feed.html)**

: 

Feed tracking is available for the object.

**[BatchJobPartFailedRecordHistory](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-associated-objects-history.html)**

: 

History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/sforce-api-objects-batchjobpartfailedrecord.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
