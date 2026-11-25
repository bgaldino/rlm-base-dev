---
page_id: sforce-api-objects-pricebookentryderivedprice
title: PriceBookEntryDerivedPrice
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebookentryderivedprice.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_pricebookentryderivedprice.htm
fetched_at: 2026-11-25
---

# PriceBookEntryDerivedPrice

Represents the price of a product that’s derived from another source such as a product or an asset. This object is available in API version 61.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### ContributingProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: Source product from which the derived price is calculated. The source product is associated with the derived price product.

This field is a relationship field.

- **Relationship Name**: ContributingProduct

- **Relationship Type**: Lookup

- **Refers To**: Product2

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: ISO code for any currency allowed by the organization. Available only if the multicurrency feature is enabled.

Valid values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar.

The default value is `USD`.

### DerivedPricingScope

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Scope of the product based on which the derived price is calculated.

Valid values are `Both`, `NonTransactional`, or `Transactional`.

### EffectiveFrom

- **Type**: dateTime

- **Properties**: Create, Filter, Sort, Update

- **Description**: Date and time when the derived pricing comes into effect.

### EffectiveTo

- **Type**: dateTime

- **Properties**: Create, Filter, Nillable, Sort, Update

- **Description**: Date and time when the derived pricing is no longer in effect.

### Formula

- **Type**: string

- **Properties**: Create, Filter, Sort, Update

- **Description**: Coded format of the formula used to calculate the derived price of a product from another product or asset.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (`LastReferencedDate`) and not viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Name of the derived price record.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: ID of the user who created the record.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Relationship Type**: Lookup

- **Refers To**: Group, User

### PricebookEntryId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**: Price book entry associated with the source product.

This field is a relationship field.

- **Relationship Name**: PricebookEntry

- **Relationship Type**: Lookup

- **Refers To**: PricebookEntry

### PricebookId

- **Type**: reference

- **Properties**: Create, Filter, Group, Nillable, Sort

- **Description**: Price book associated with the source product.

This field is a relationship field.

- **Relationship Name**: Pricebook

- **Relationship Type**: Lookup

- **Refers To**: Pricebook2

### PricingSource

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: Pricing type used to calculate the derived price of the product.

Valid values are `Header` or `Product`.

### ProductId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Product associated with the derived pricing.

This field is a relationship field.

- **Relationship Name**: Product

- **Relationship Type**: Lookup

- **Refers To**: Product2

### ProductSellingModelId

- **Type**: reference

- **Properties**: Filter, Group, Sort

- **Description**: Product selling model associated with this record.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Relationship Type**: Lookup

- **Refers To**: ProductSellingModel

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[PriceBookEntryDerivedPriceFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[PriceBookEntryDerivedPriceHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[PriceBookEntryDerivedPriceShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricebookentryderivedprice.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
