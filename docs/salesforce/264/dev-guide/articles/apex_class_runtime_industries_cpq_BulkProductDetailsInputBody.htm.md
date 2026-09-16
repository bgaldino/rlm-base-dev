---
page_id: apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm
title: BulkProductDetailsInputBody Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BulkProductDetailsInputBody Class

Contains the details of the request to retrieve product details by using product ID and
    product selling model ID.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[BulkProductDetailsInputBody Properties](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBody_properties)**  

Contains properties to retrieve details of products.

  

## BulkProductDetailsInputBody Properties

  
  
  
Contains properties to retrieve details of products.

    
      

The `BulkProductDetailsInputBody` class includes these
        properties.

    

    
  

- 
**[productId](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBody_productId)**  

Set the ID of the product to return the details for.

- 
**[productSellingModelId](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_ricpq_BulkProductDetailsInputBody_productSellingModelId)**  

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
