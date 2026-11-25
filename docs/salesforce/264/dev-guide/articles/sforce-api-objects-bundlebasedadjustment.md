---
page_id: sforce-api-objects-bundlebasedadjustment
title: BundleBasedAdjustment
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bundlebasedadjustment.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_bundlebasedadjustment.htm
fetched_at: 2026-11-25
---

# BundleBasedAdjustment

Represents the association between the product selling model and the price adjustment for a product or service being sold as a bundle. This object stores information of the product or service’s price, the discounts applied, along with its value for a given date range. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### AdjustmentType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The type of pricing adjustment being made.

Possible values are `Amount`, `Override`, or `Percentage`.

### AdjustmentValue

- **Type**: double

- **Properties**: Create, Filter, Sort, Update

- **Description**: The type of pricing adjustment being made.

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: ISO code of the currency. Must be one of the valid alphabetic, three-letter currency ISO codes defined by the ISO 4217 standard, such as USD, GBP, or JPY. Must be unique within your organization.

Possible values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar.

The default value is `USD`.

### EffectiveFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: The date and time when the bundle based adjustment comes into effect.

### EffectiveTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time till when the bundle based adjustment remains effective.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the bundle based adjustment was last referenced.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The date the bundle based adjustment was last viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the bundle based adjustment record.

### ParentProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Represents the immediate parent in the product bundle that the price is configured for.

This field is a relationship field.

- **Relationship Name**: ParentProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

### ParentProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The immediate parent node of a product selling model when nodes are represented in a hierarchial structure.

This field is a relationship field.

- **Relationship Name**: ParentProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

### PriceAdjustmentScheduleId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The price adjustment schedule associated with the bundle based adjustment record.

This field is a relationship field.

- **Relationship Name**: PriceAdjustmentSchedule

- **Relationship Type**: Lookup

- **Refers To**: PriceAdjustmentSchedule

### PricingTerm

- **Type**: int

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The number of pricing term units in the pricing term. Used with PricingTermUnit to define the length of the pricing term. For example, if PricingTermUnit is Months and this field is 1, the subscription is priced monthly.If the selling model is one-time, this field must be null.

### PricingTermUnit

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The unit of time used to define the pricing term. Used with PricingTerm to define the length of the pricing term. For example, if this field is Months and PricingTerm is 1, the subscription is priced monthly. If the selling model is one-time, this field must be null.

Possible values are `Annual`—Years, `Months`, `Quarterly`, or `Semi-Annual`.

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The ID of the product associated with the product bundle set.

This field is a relationship field.

- **Relationship Name**: Product

- **Relationship Type**: Lookup

- **Refers To**: Product2

### ProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The ID of the ProductSellingModel record associated with this bundle based adjustment record.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

### RootBundleId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Represents the structural root product in a product’s bundle that the price is configured for.

This field is a relationship field.

- **Relationship Name**: RootBundle

- **Relationship Type**: Lookup

- **Refers To**: Product2

### RootProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: The root product selling model. The primary or base product selling method.

This field is a relationship field.

- **Relationship Name**: RootProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

### SellingModelType

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Indicates whether the product is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term.

Possible values are `Evergreen`, `OneTime`—One Time, or `TermDefined`—Term-Defined.

The default value is `OneTime`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[BundleBasedAdjustmentFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[BundleBasedAdjustmentHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-bundlebasedadjustment.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
