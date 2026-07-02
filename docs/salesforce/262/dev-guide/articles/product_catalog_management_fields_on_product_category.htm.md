---
page_id: product_catalog_management_fields_on_product_category.htm
title: Product Catalog Management Fields on Product Category
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_category.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Fields on Product Category

Standard and custom fields extend the standard Product Category
object for use in Product Catalog Management.

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  A unique ID associated with the catalog. The maximum size is 80 alphanumeric characters. |
| IsNavigational | Type  boolean  Properties  Create, Defaulted on create, Filter, Group, Sort, Update  Description  Indicates whether the category or subcategory is shown in the menu as a navigational breadcrumb (`true`) or not (`false`). Available in API version 62.0 and later.  The default value is `false`. |

#### See Also

- [Product Category](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_productcategory.htm "Product Category - HTML (New Window)")
