---
page_id: apex_class_ricpq_ProductSellingModelOptionOR.htm
title: ProductSellingModelOptionOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_ricpq_ProductSellingModelOptionOR.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductSellingModelOptionOutputRepresentation Class

Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductSellingModelOptionOutputRepresentation Properties](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_ricpq_ProductSellingModelOptionOR_properties)**  

Learn more about the properties available with the     ProductSellingModelOptionOutputRepresentation class.

  

## ProductSellingModelOptionOutputRepresentation Properties

  
  
  
Learn more about the properties available with the
    ProductSellingModelOptionOutputRepresentation class.

    
      

The  `ProductSellingModelOptionOutputRepresentation` class
        includes these properties.

    

    
  

- 
**[id](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_id)**  

Get or set the unique identifier of the product selling model option.

- 
**[productId](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_ricpq_ProductSellingModelOptionOR_productId)**  

Get or set the identifier of the product that this selling model option applies to.

- 
**[productSellingModel](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_ricpq_ProductSellingModelOptionOR_productSellingModel)**  

Get or set the product selling model details for this option.

- 
**[productSellingModelId](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_ricpq_ProductSellingModelOptionOR_productSellingModelId)**  

Get or set the identifier of the product selling model for this option.

### id

Get or set the unique identifier of the product selling model option.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### productId

Get or set the identifier of the product that this selling model option applies to.

#### Signature

`public String productId {get; set;}`

#### Property Value

Type: String

### productSellingModel

Get or set the product selling model details for this option.

#### Signature

`public runtime_industries_cpq.ProductSellingModelOutputRepresentation productSellingModel {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductSellingModelOutputRepresentation

### productSellingModelId

Get or set the identifier of the product selling model for this option.

#### Signature

`public String productSellingModelId {get; set;}`

#### Property Value

Type: String
