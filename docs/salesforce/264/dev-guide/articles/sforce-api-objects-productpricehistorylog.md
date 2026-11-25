---
page_id: sforce-api-objects-productpricehistorylog
title: ProductPriceHistoryLog
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productpricehistorylog.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_productpricehistorylog.htm
fetched_at: 2026-11-25
---

# ProductPriceHistoryLog

Stores historical pricing data based on the product’s price range. This object is available in API version 62.0 and later.

**Important:**

Where possible, we changed noninclusive terms to align with our company value of Equality. We maintained certain terms to avoid any effect on customer implementations.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CurrencyIsoCode

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: ISO code for any currency allowed by the organization. Available only for organizations with the multicurrency feature enabled.

Valid values are `BHD`—Bahraini Dinar, `JPY`—Japanese Yen, or `USD`—U.S. Dollar.

The default value is `USD`.

### Date

- **Type**: date

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The date when the product price history log record is created.

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates whether the product price history log has been archived (`true`) or not (`false`). This field is read-only.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: The timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (`LastReferencedDate`) and not viewed.

### Name

- **Type**: string

- **Properties**: Autonumber, Defaulted on create, Filter, idLookup, Sort

- **Description**: Required. The name of the product price history log.

### ProductPriceRangeId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort

- **Description**:

The product price range associated with this product price history log record.

This field is a relationship field.

- **Relationship Name**: ProductPriceRange

- **Relationship Type**: Master-detail

- **Refers To**: ProductPriceRange (the master object)

### TrackedPrice

- **Type**: currency

- **Properties**: Create, Filter, Sort, Update

- **Description**: The price for a product recorded for a particular date.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

**[ProductPriceHistoryLogFeed](./sforce-api-associated-objects-feed.md):** Feed tracking is available for the object.

**[ProductPriceHistoryLogHistory](./sforce-api-associated-objects-history.md):** History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productpricehistorylog.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
