---
page_id: sforce-api-objects-pricing-contractitemprice
title: ContractItemPrice
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricing-contractitemprice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_pricing_contractitemprice.htm
fetched_at: 2026-11-25
---

# ContractItemPrice

Represents the price of a product on the contract. This object is available in API version 61.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `undelete()`, `update()`, `upsert()`

## Fields

### ContractId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: The contract record associated with this contract item price record.

This field is a relationship field.

- **Relationship Name**: Contract

- **Relationship Type**: Master-detail

- **Refers To**: Contract (the master object)

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Restricted picklist, Sort

- **Description**: Contains the ISO code for any currency allowed by the organization. Available only if the multicurrency feature is enabled.

Valid value is `USD`—U.S. Dollar

The default value is `USD`.

### DiscountType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The unit of the discount.

Valid values are `AdjustmentAmount` or `AdjustmentPercentage`.

### DiscountValue

- **Type**: double

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The value of the discount.

### EndDate

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The date and time till when the contract item price is no longer in effect.

### ItemId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The ID of the line item record associated with this contract item price record.

This field is a polymorphic relationship field.

- **Relationship Name**: Item

- **Relationship Type**: Lookup

- **Refers To**: Product2, ProductCategory

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed a record related to this record.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: The name of the contract item price record.

### Price

- **Type**: currency

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: The unit price of the product that’s being sold as part of the contract.

### ProductSellingModelId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The ID of the product selling model record associated with this contract item price record.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

### SellingModelType

- **Type**: picklist

- **Properties**: Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Specifies whether the line item is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term.

Valid values are `Evergreen`, `OneTime`, or `TermDefined`.

The default value is `OneTime`.

### StartDate

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: The date and time when the contract item price comes into effect.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ContractItemPriceFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ContractItemPriceHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricing-contractitemprice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
