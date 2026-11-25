---
page_id: sforce-api-objects-assetfulfillmentdecomp
title: AssetFulfillmentDecomp
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-assetfulfillmentdecomp.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_assetfulfillmentdecomp.htm
fetched_at: 2026-11-25
---

# AssetFulfillmentDecomp

Represents the relationship between an ordered asset and its corresponding fulfillment asset. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### FulfillmentSourceAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The identifier of the relationship between an asset and a fulfillment asset.

This field is a polymorphic relationship field.

- **Relationship Name**: FulfillmentSourceAsset

- **Refers To**: Asset, FulfillmentAsset

### FulfillmentTargetAssetId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The identifier of the target asset that’s being fulfilled.

This field is a relationship field.

- **Relationship Name**: FulfillmentTargetAsset

- **Refers To**: FulfillmentAsset

### IsUsedForFulfmtAssetActivation

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates if internal jobs are allowed to activate the related fulfillment asset. The default value is true.

This field is available in API version 6.0 and later.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the asset that’s being fulfilled.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who created the request record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### RelationshipType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of relationship between an asset and a fulfillment asset.

Valid values are `SourceBundleRoot` or `SourceLineItem`.

### SegmentIdentifier

- **Type**: string

- **Properties**: Create, Group, Nillable, Sort,

- **Description**: The ID of the ramp segment associated with the asset state period.

This field is available in API version 63.0 and later in orgs that have Revenue Management when the Ramp Deals setting is enabled.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The status of the fulfillment asset.

Valid values are `Active` or `Inactive`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[AssetFulfillmentDecompHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object starting API version 65.0.

**[AssetFulfillmentDecompShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-assetfulfillmentdecomp.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
