---
page_id: apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm
title: BulkProductDetailsInputBody Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# BulkProductDetailsInputBody Class

Contains the details of the request to retrieve product details by using product ID and
product selling model ID.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[BulkProductDetailsInputBody Properties](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBody_properties)**  
  Contains properties to retrieve details of products.

## BulkProductDetailsInputBody Properties

Contains properties to retrieve details of products.

The `BulkProductDetailsInputBody` class includes these
properties.

- **[productId](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBody_productId)**  
  Set the ID of the product to return the details for.
- **[productSellingModelId](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBody_productSellingModelId)**  
  Set the ID of the product selling model to return the details for.

### productId

Set the ID of the product to return the details for.

#### Signature

`public String productId {get; set;}`

#### Property Value

Type: String

### productSellingModelId

Set the ID of the product selling model to return the details for.

#### Signature

`public String productSellingModelId {get; set;}`

#### Property Value

Type: String
