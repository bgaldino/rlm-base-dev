---
page_id: product_catalog_management_fields_on_product_related_component.htm
title: Product Catalog Management Fields on Product Related Component
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_related_component.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-11-23
---

# Product Catalog Management Fields on Product Related Component

Standard and custom fields extend the standard Product Related Component
object for use in Product Catalog Management.

#### See Also

- [Product Related Component](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productrelatedcomponent.htm "Product Related Component - HTML (New Window)")

## Fields

### ChildProductClassificationId

**Type:** reference

**Properties:** Create, Filter, Group, Nillable, Sort

**Description:** The child product classification that's associated with a product.

This field is a relationship field.

**Relationship Name:** ChildProductClassification

**Refers To:** ProductClassification

### QuoteVisibility

**Type:** picklist

**Properties:** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update

**Description:** Specifies the product-related component to display as a quote line item in the Transaction Line Editor and the quote document. The default value is Always.

Possible values are:

- Always
- Transaction Line Editor Only
- Quote Document Only
- Never

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_related_component.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
