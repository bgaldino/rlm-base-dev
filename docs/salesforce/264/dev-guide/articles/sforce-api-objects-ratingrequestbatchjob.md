---
page_id: sforce-api-objects-ratingrequestbatchjob
title: RatingRequestBatchJob
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingrequestbatchjob.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-std-objects-parent
legacy_page_id: sforce_api_objects_ratingrequestbatchjob.htm
fetched_at: 2026-11-25
---

# RatingRequestBatchJob

Represents a junction between the rating request and batch job objects. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### BatchJobId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: ID of the batch job that triggered the rating request on the aggregated records.

This field is a relationship field.

- **Relationship Name**: BatchJob

- **Refers To**: BatchJob

### ErrorCode

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Error code that defines the batch job failure.

Valid values are `BadRequest` or `InternalError`.

### ErrorMessage

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Error message that describes the cause of the batch job failure.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Name of the rating request batch job record.

### RatingRequestId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: ID of the rating request record associated with the batch job.

This field is a relationship field.

- **Relationship Name**: RatingRequest

- **Relationship Type**: Master-detail

- **Refers To**: RatingRequest (the master object)

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[RatingRequestBatchJobFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[RatingRequestBatchJobHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-ratingrequestbatchjob.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
