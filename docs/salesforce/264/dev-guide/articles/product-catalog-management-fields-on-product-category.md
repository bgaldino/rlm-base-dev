---
page_id: product-catalog-management-fields-on-product-category
title: Product Catalog Management Fields on Product Category
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-fields-on-product-category.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-fields-on-standard-objects
legacy_page_id: product_catalog_management_fields_on_product_category.htm
fetched_at: 2026-11-25
---

# Product Catalog Management Fields on Product Category

Standard and custom fields extend the standard Product Category object for use in Product Catalog Management.

**See Also**

- [Product Category](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_productcategory.htm)

## Fields

### Code

**Type:** string

**Properties:** Create, Filter, Group, idLookup, Nillable, Sort, Update

**Description:** A unique ID associated with the catalog. The maximum size is 80 alphanumeric characters.

### IsNavigational

**Type:** boolean

**Properties:** Create, Defaulted on create, Filter, Group, Sort, Update

**Description:** Indicates whether the category or subcategory is shown in the menu as a navigational breadcrumb (`true`) or not (`false`). Available in API version 62.0 and later.

The default value is `false`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-catalog-management-fields-on-product-category.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
