---
page_id: sforce-api-objects-usageresource
title: UsageResource
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usageresource.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-std-objects-parent
legacy_page_id: sforce_api_objects_usageresource.htm
fetched_at: 2026-11-25
---

# UsageResource

Represents an entitlement granted to a user or party by a provider, such as data storage, computing power, bandwidth, or any other product or service. Additionally, this object is used to represent resources consumed over time. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### Category

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The category of the usage resource that’s used to organize and understand the product grant maps.

Valid values are `Currency`—Available in API version 65.0 and later, `Usage`, or `Token`—Available in API version 64.0 and later.

### Code

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The unique user-defined string for the usage resource.

### DefaultUnitOfMeasureId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The default unit of measure for the given resource. The default value can be overridden with an alternate default unit of measure for a given resource.

This field is a relationship field.

- **Relationship Name**: DefaultUnitOfMeasure

- **Refers To**: UnitOfMeasure

### Description

- **Type**: string

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The description of the usage resource.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date when this record was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name of the usage resource record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The ID of the owner of the usage resource record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### Status

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The status of the usage resource.

Valid values are `Active`, `Draft`, or `Inactive`.

### TokenResourceId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The usage resource of Category `Token` that’s used to charge this usage resource. For example, you can select a usage resource Credits (Token category) to rate the usage resource Data (Usage category). This field is available in API version 65.0 and later.

- **Relationship Name**: TokenResource

- **Refers To**: UsageResource

### UnitOfMeasureClassId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The unit of measure class that’s used with the resource to define the units in which this resource is measured.

This field is a relationship field.

- **Relationship Name**: UnitOfMeasureClass

- **Refers To**: UnitOfMeasureClass

### UsageDefinitionProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The product associated with the usage resource to retrieve tax policy, calculate rating during overages, and other invoicing actions.

This field is a relationship field.

- **Relationship Name**: UsageDefinitionProduct

- **Refers To**: Product2

## Associated Objects

This object has these associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[UsageResourceFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[UsageResourceHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[UsageResourceOwnerSharingRule](./sforce-api-associated-objects-ownersharingrule.md):** Sharing rules are available for the object.

**[UsageResourceShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-usageresource.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
