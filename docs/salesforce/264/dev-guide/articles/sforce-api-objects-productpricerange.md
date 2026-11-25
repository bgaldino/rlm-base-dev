---
page_id: sforce-api-objects-productpricerange
title: ProductPriceRange
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productpricerange.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_productpricerange.htm
fetched_at: 2026-11-25
---

# ProductPriceRange

Represents the price range of a product determined by using a product selling model that’s stored in the relevant price book. This object is available in API version 62.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: ISO code for any currency allowed by the organization. Available only for organizations with the multicurrency feature enabled.

Valid values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar.

The default value is `USD`.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates whether the product price range has been archived (`true`) or not (`false`). This field is read-only.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (`LastReferencedDate`) and not viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The name of the product price range.

### OwnerId

- **Type**: reference

- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update

- **Description**: The Salesforce ID of the sales representative who owns the product price range.

This field is a polymorphic relationship field.

- **Relationship Name**: Owner

- **Refers To**: Group, User

### ProductId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The product for which the price range is being determined.

This field is a relationship field.

- **Relationship Name**: Product

- **Refers To**: Product2

### ProductSellingModelId

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: The product selling model used to determine the price range of the product.

This field is a relationship field.

- **Relationship Name**: ProductSellingModel

- **Refers To**: ProductSellingModel

### RecordedPrice

- **Type**: currency

- **Properties**: Filter, Nillable, Sort

- **Description**: The selected price of the product over a range of prices.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductPriceRangeFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductPriceRangeHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

**[ProductPriceRangeShare](./sforce-api-associated-objects-share.md):** Sharing is available for the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productpricerange.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
