---
page_id: sforce-api-objects-fulfillmentplan
title: FulfillmentPlan
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentplan.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentplan.htm
fetched_at: 2026-11-25
---

# FulfillmentPlan

Represents a set of steps to be created to fulfill the order. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### ExecutionUserId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: For internal use only.

- **Relationship Name**: ExecutionUser

- **Refers To**: User

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user referenced this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The most recent date when a user viewed this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the fulfillment plan.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### Priority

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The priority of the fulfillment plan execution. This field is available in API version 63.0 and later.

Valid values are `Default`, `High`, or `Bulk`.

### SourceIdentifier

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update, idLookup (Available in API version 64.0 and later)

- **Description**: For internal use only.

### SourceType

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The type of source for the fulfillment plan. This field is available in API version 62.0 and later.

### State

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The status of the fulfillment plan.

Valid values are `Completed`, `InProgress`, or `NotStarted`.

### UsageType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The business that uses Fulfillment Orchestration.

Valid values are `IntegrationOrchestrator`, `Generic`, or `StageManagement`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentPlanChangeEvent](./sforce-api-associated-objects-change-event.md):** Change events are available for the object.

**[FulfillmentPlanHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object starting API version 65.0.

**[FulfillmentPlanShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentplan.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
