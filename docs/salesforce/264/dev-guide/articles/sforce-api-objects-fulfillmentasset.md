---
page_id: sforce-api-objects-fulfillmentasset
title: FulfillmentAsset
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentasset.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_fulfillmentasset.htm
fetched_at: 2026-11-25
---

# FulfillmentAsset

Represents an instance of a technical product used to provide a customer asset. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AccountId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The identifier of the account.

This field is a relationship field.

- **Relationship Name**: Account

- **Relationship Type**: Lookup

- **Refers To**: Account

### IsTimeAware

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates if the fulfillment asset’s configuration data is tracked in a time-aware or time-agnostic manner. Available in API version 67.0 and later.

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **For internal use only.**:

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **For internal use only.**:

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the fulfillment asset.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: For internal use only.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The identifier of the corresponding product.

This field is a relationship field.

- **Relationship Name**: Product

- **Relationship Type**: Lookup

- **Refers To**: Product2

### Quantity

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: For internal use only.

### ScopeIdentifierText

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Nillable, Sort

- **Description**: The scope in which this fulfillment asset record is created. This field is available in API version 65.0 and later.

### StateEndTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Represents the end time of the current fulfillment asset state period. Available in API version 67.0 and later.

### StateStartTime

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Represents the start time of the current fulfillment asset state period. Available in API version 67.0 and later.

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The status of the fulfillment asset.

Valid values are `Active` or `InActive`.

### UnitOfMeasureId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The unit of measure for the asset quantity such as, unit, gallon, ton, or case. This field is available in API version 63.0 and later.

This field is a relationship field.

- **Relationship Name**: UnitOfMeasure

- **Refers To**: UnitOfMeasure

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[FulfillmentAssetHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object starting API version 65.0.

**[FulfillmentAssetShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-fulfillmentasset.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
