---
page_id: sforce-api-objects-priceadjustmentschedule
title: PriceAdjustmentSchedule
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-priceadjustmentschedule.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_priceadjustmentschedule.htm
fetched_at: 2026-11-25
---

# PriceAdjustmentSchedule

Represents a series of tiered discounts based on the number of items purchased.  This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AdjustmentMethod

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The method for applying tiered pricing. Possible values are Range—All items receive the discount of the highest tier the quantity falls in. or Slab—Items receive the discount defined for the tier they fall in. Possible values are `Range` or `Slab` The default value is `Range`.

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: Available only if the multicurrency feature is enabled. Contains the ISO code for any currency allowed by the organization. Possible values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar The default value is `USD`.

### Description

- **Type**: textarea

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: Text description of the price adjustment schedule.

### EffectiveFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the price adjustment schedule comes into effect.

### EffectiveTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time when the price adjustment schedule remains effective.

### IsActive

- **Type**: boolean

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: Indicates whether the price adjustment schedule is active (true) or not (false). You can change this field’s value as often as necessary. Label is **Active**. Default value is `False`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates whether the price adjustment schedule has been archived (true) or not (false). This field is read-only.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: Required. The name of the price adjustment schedule. This field is read-only. Label is Price Adjustment Schedule Name.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The Salesforce ID of the sales representative who owns the price adjustment schedule. This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### Pricebook2Id

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The price book associated with this price adjustment schedule record. This field is a relationship field.

- **Relationship Name**: Pricebook2

- **Relationship Type**: Lookup

- **Refers To**: Pricebook2

### ScheduleType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of price adjustment schedule. Possible values are `Attribute`, `Bundle`, `Custom`, `Term`, or `Volume` The default value is `Volume`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

[PriceAdjustmentScheduleShare](./sforce-api-associated-objects-share.md): Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-priceadjustmentschedule.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
