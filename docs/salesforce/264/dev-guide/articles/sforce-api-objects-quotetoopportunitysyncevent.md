---
page_id: sforce-api-objects-quotetoopportunitysyncevent
title: QuoteToOpportunitySyncEvent
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotetoopportunitysyncevent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: quote-and-order-capture-standard-objects
legacy_page_id: sforce_api_objects_quotetoopportunitysyncevent.htm
fetched_at: 2026-11-25
---

# QuoteToOpportunitySyncEvent

Represents an asynchronous quote to opportunity synchronization event. It tracks whether the sync succeeded or failed and notifies associated subscribers upon completion. This object is available in API version XX.0 and later.

## Supported Calls

`create()`, `describeSObjects()`

## Fields

### CorrelationIdentifier

- **Type**: string

- **Properties**: Create, Nillable

- **Description**: The caller-specified ID that matches this event to the originating request.

### ErrorCode

- **Type**: string

- **Properties**: Create, Nillable

- **Description**: The error code returned when the sync fails. Null when Has Errors is False.

### ErrorMessage

- **Type**: textarea

- **Properties**: Create, Nillable

- **Description**: The error message that explains why the sync failed. Null when Has Errors is False.

### HasErrors

- **Type**: boolean

- **Properties**: Create, Defaulted on create

- **Description**: Indicates whether the sync failed. True if the sync completed with errors or False if the sync succeeded.

The default value is `false`.

### OpportunityRecordId

- **Type**: reference

- **Properties**: Create, Nillable

- **Description**: The ID of the Opportunity record being synced. Null if the sync fails before an Opportunity is associated.

This field is a relationship field.

- **Relationship Name**: OpportunityRecord

- **Refers To**: Opportunity

### QuoteRecordId

- **Type**: reference

- **Properties**: Create

- **Description**: The ID of the Quote record synced to its related Opportunity.

This field is a relationship field.

- **Relationship Name**: QuoteRecord

- **Refers To**: Quote

### RequestIdentifier

- **Type**: string

- **Properties**: Create, Nillable

- **Description**: The unique identifier for the request that triggered this sync event.

### RevenueTransactionErrLogId

- **Type**: reference

- **Properties**: Create, Nillable

- **Description**: The ID of the Revenue Transaction Error Log record created when the sync fails. Null when Has Errors is False.

This field is a relationship field.

- **Relationship Name**: RevenueTransactionErrLog

- **Refers To**: RevenueTransactionErrorLog

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-quotetoopportunitysyncevent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
