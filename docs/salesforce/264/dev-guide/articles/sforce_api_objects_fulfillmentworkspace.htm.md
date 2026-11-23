---
page_id: sforce_api_objects_fulfillmentworkspace.htm
title: FulfillmentWorkspace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentworkspace.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-11-23
---

# FulfillmentWorkspace

Represents a visual designer for fulfillment plans that can have multiple step groups and their dependencies. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### Description

- **Type**: textarea
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The description of the fulfillment workspace.

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
- **Properties**: Create, Filter, Group, idLookup, Sort, Update
- **Description**: The name of the fulfillment workspace.

### OwnerId

- **Type**: reference
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: The ID of the user who owns this record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner
- **Refers To**: Group, User

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentWorkspaceHistory](./sforce_api_associated_objects_history.htm.md "StandardObjectNameHistory is the model for all history objects associated with standard objects. These objects represent the history of changes to the values in the fields of a standard object."):** History is available for tracked fields of the object starting API version 65.0.

**[FulfillmentWorkspaceShare](./sforce_api_associated_objects_share.htm.md "StandardObjectNameShare is the model for all share objects associated with standard objects. These objects represent a sharing entry on the standard object."):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentworkspace.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
