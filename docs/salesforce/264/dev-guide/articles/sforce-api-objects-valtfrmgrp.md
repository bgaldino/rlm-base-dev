---
page_id: sforce-api-objects-valtfrmgrp
title: ValTfrmGrp
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-valtfrmgrp.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Dynamic Revenue Orchestrator
parent_page: dynamic-revenue-orchestrator-std-objects-parent
legacy_page_id: sforce_api_objects_valtfrmgrp.htm
fetched_at: 2026-11-25
---

# ValTfrmGrp

Represents a rule that determines how an order is broken into sub-orders with specific technical details that help in order fulfillment. The rule can be applied to a commercial or a technical product. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### DestinationPrimitiveType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The data type of the output value.

Valid values are:

- `Boolean`

- `Currency`

- `Date`

- `Datetime`

- `Number`

- `Percent`—Picklist Value

- `Text`

### IsDestinationEnumerated

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the output is a list of values (`true`) or not (`false`).

The default value is `false`.

### IsSourceEnumerated

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the input is from a list of values (`true`) or not (`false`).

The default value is `false`.

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

- **Description**: The name of the list mapping.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the user who owns this record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### SourcePrimitiveType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The data type of the input value.

Valid values are:

- `Boolean`

- `Currency`

- `Date`

- `Datetime`

- `Number`

- `Percent`—Picklist Value

- `Text`

### UsageType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The data mapping feature that uses this value transformation group.

Valid value is `DFOListMapping`

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ValTfrmGrpShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-valtfrmgrp.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
