---
page_id: sforce-api-objects-pricingprocedureresolution
title: PricingProcedureResolution
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocedureresolution.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_pricingprocedureresolution.htm
fetched_at: 2026-11-25
---

# PricingProcedureResolution

Represents a selection for a pricing procedure to execute a pricing process from a list of pricing procedures available. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization.

Possible values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar.

The default value is `USD`.

### EffectiveFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: The date and time when the pricing procedure resolution comes into effect.

### EffectiveTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time till when the pricing procedure resolution remains effective.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates whether the pricing procedure resolution has been archived (true) or not (false). This field is read-only.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The name of the pricing procedure resolution.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The Salesforce ID of the sales representative who owns the pricing procedure resolution.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### PricingProcedureId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The pricing procedure record associated with this pricing procedure resolution.

This field is a relationship field.

- **Relationship Name**: PricingProcedure

- **Relationship Type**: Lookup

- **Refers To**: ExpressionSet

### ProcedureType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The pricing data store associated with this pricing recipe field mappings.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PricingProcedureResolutionFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[PricingProcedureResolutionHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[PricingProcedureResolutionShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocedureresolution.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
