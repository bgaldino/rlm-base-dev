---
page_id: apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm
title: BulkProductDetailsInputBodyList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BulkProductDetailsInputBodyList Class

Contains details of the request to retrieve a list of products.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[BulkProductDetailsInputBodyList Properties](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBodyList_properties)**  

Contains properties to retrieve details of a list of products.

  

## BulkProductDetailsInputBodyList Properties

  
  
  
Contains properties to retrieve details of a list of products.

    
      

The `BulkProductDetailsInputBodyList` class includes these
        properties.

    

    
  

- 
**[productData](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm.md#apex_runtime_industries_cpq_BulkProductDetailsInputBodyList_productData)**  

Set the list of maps that contain product IDs and product selling model IDs.

### productData

Set the list of maps that contain product IDs and product selling model IDs.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsInputBody> productData {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.BulkProductDetailsInputBody](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md#apex_class_runtime_industries_cpq_BulkProductDetailsInputBody)>
