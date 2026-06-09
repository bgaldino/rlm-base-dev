---
page_id: apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm
title: BulkProductDetailsInputBodyList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# BulkProductDetailsInputBodyList Class

Contains details of the request to retrieve a list of products.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[BulkProductDetailsInputBodyList Properties](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBodyList_properties)**  
  Contains properties to retrieve details of a list of products.

## BulkProductDetailsInputBodyList Properties

Contains properties to retrieve details of a list of products.

The `BulkProductDetailsInputBodyList` class includes these
properties.

- **[productData](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBodyList_productData)**  
  Set the list of maps that contain product IDs and product selling model IDs.

### productData

Set the list of maps that contain product IDs and product selling model IDs.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsInputBody> productData {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.BulkProductDetailsInputBody](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_class_runtime_industries_cpq_BulkProductDetailsInputBody "Contains the details of the request to retrieve product details by using product ID and product selling model ID.")>
