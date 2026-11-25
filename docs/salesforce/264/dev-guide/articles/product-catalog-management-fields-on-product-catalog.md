---
page_id: product-catalog-management-fields-on-product-catalog
title: Product Catalog Management Fields on Product Catalog
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-fields-on-product-catalog.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-fields-on-standard-objects
legacy_page_id: product_catalog_management_fields_on_product_catalog.htm
fetched_at: 2026-11-25
---

# Product Catalog Management Fields on Product Catalog

Standard and custom fields extend the standard Product Catalog object for use in Product Catalog Management. This object is available in API version 60.0 and later.

**See Also**

- [Product Catalog](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_productcatalog.htm)

## Fields

### Code

**Type:** string

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

**Description:** A unique ID associated with the catalog. The maximum size is 80 alphanumeric characters.

### Description

**Type:** textarea

**Properties:** Create, Nillable, Update

**Description:** The description of the catalog that’s used during design time. The maximum size is 255 alphanumeric characters.

### EffectiveEndDate

**Type:** dateTime

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The date after which the product catalog is unavailable to end users.

### EffectiveStartDate

**Type:** dateTime

**Properties:** Create, Filter, Nillable, Sort, Update

**Description:** The date on which the product catalog is available to end users.

### CatalogType

**Type:** picklist

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** The category of an entry in the catalog.

Possible values are:

- `Sales`

- `ServiceProcess`—Service Process

The default value is `Sales`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-fields-on-product-catalog.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
