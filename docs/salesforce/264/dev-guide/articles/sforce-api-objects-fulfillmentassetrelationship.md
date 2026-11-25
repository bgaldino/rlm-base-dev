---
page_id: sforce-api-objects-fulfillmentassetrelationship
title: FulfillmentAssetRelationship
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetrelationship.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentassetrelationship.htm
fetched_at: 2026-11-25
---

# FulfillmentAssetRelationship

Represents a relationship between two fulfillment assets. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### AssociatedFulfillAssetRole

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The role of the associated fulfillment asset.

Valid values are `BundleComponent` or `ClassificationComponent`—Product Classification Component.

### AssociatedFulfillmentAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The name of the associated fulfillment asset.

This field is a relationship field.

- **Relationship Name**: AssociatedFulfillmentAsset

- **Refers To**: FulfillmentAsset

### EndTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The time until when this asset relationship is valid.

### MainFulfillmentAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The name of the primary fulfillment asset.

This field is a relationship field.

- **Relationship Name**: MainFulfillmentAsset

- **Relationship Type**: Master-detail

- **Refers To**: FulfillmentAsset (the master object)

### MainFulfillmentAssetRole

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The role of the primary fulfillment asset.

Valid value is `Bundle Parent`.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the fulfillment asset relationship.

### ProductRelationshipTypeId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The type of relationship between two assets.

This field is a relationship field.

- **Relationship Name**: ProductRelationshipType

- **Refers To**: ProductRelationshipType

### StartTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The time from when this asset relationship is valid.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentassetrelationship.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
