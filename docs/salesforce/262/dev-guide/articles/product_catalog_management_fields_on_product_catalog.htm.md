---
page_id: product_catalog_management_fields_on_product_catalog.htm
title: Product Catalog Management Fields on Product Catalog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_catalog.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Fields on Product Catalog

Standard and custom fields extend the standard Product Catalog object
for use in Product Catalog Management. This object is available in API version 60.0
and later.

## Fields

| Field | Details |
| --- | --- |
| Code | Type  string  Properties  Create, Filter, Group, idLookup, Nillable, Sort, Update  Description  A unique ID associated with the catalog. The maximum size is 80 alphanumeric characters. |
| Description | Type  textarea  Properties  Create, Nillable, Update  Description  The description of the catalog that's used during design time. The maximum size is 255 alphanumeric characters. |
| EffectiveEndDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date after which the product catalog is unavailable to end users. |
| EffectiveStartDate | Type  dateTime  Properties  Create, Filter, Nillable, Sort, Update  Description  The date on which the product catalog is available to end users. |
| CatalogType | Type  picklist  Properties  Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update  Description  The category of an entry in the catalog.  Possible values are:  - `Sales` - `ServiceProcess`—Service Process  The default value is `Sales`. |

#### See Also

- [Product Catalog](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_productcatalog.htm "Product Catalog - HTML (New Window)")
