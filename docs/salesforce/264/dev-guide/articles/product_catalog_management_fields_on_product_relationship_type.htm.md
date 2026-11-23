---
page_id: product_catalog_management_fields_on_product_relationship_type.htm
title: Product Catalog Management Fields on Product Relationship Type
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_relationship_type.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-11-23
---

# Product Catalog Management Fields on Product Relationship Type

Standard and custom fields extend the standard Product Relationship Type
object for use in Product Catalog Management.

#### See Also

- [Product Relationship Type](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productrelationshiptype.htm "Product Relationship Type - HTML (New Window)")

## Fields

### AssociatedProductRoleCat

**Type:** picklist

**Properties:** Create, Filter, Group, Nillable, Restricted picklist, Sort

**Description:** The role that the associated component plays in the relationship.

Valid values are:

- `BundleComponent`—
  The associated product is part of a bundle.
- `ClassificationComponent`— The associated
  component is a product classification. Available in API
  version 61.0 and later

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_relationship_type.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
