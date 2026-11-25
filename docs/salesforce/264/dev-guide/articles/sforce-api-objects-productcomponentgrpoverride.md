---
page_id: sforce-api-objects-productcomponentgrpoverride
title: ProductComponentGrpOverride
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productcomponentgrpoverride.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-std-objects-parent
legacy_page_id: sforce_api_objects_productcomponentgrpoverride.htm
fetched_at: 2026-11-25
---

# ProductComponentGrpOverride

Represents override information for a Product Component Group. The cardinality of the product component group can be overridden in the context of a product bundle. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Special Access Rules

Product Catalog Management must be enabled to access this object.

## Fields

### IsExcluded

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the product component group is excluded from the product bundle in the runtime. Excluding a group automatically excludes all child components of the group.

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product component override record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the product component override record was last viewed.

### MaxBundleComponents

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The maximum number of components that can be added to a group.

### MinBundleComponents

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The minimum number of components that must be added to a group.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the overridden product component group.

### OverrideContextId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The root bundle product in whose context the group cardinality is overridden.

This field is a polymorphic relationship field.

- **Relationship Name**: OverrideContext

- **Relationship Type**: Lookup

- **Refers To**: Product2

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The owner of the product component group override record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### ProductComponentGroupId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the product component group record.

This field is a relationship field.

- **Relationship Name**: ProductComponentGroup

- **Relationship Type**: Lookup

- **Refers To**: ProductComponentGroup

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productcomponentgrpoverride.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
