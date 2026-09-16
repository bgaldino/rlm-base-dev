---
page_id: apex_class_ricpq_ProductSpecificationTypeOR.htm
title: ProductSpecificationTypeOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_ricpq_ProductSpecificationTypeOR.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductSpecificationTypeOutputRepresentation Class

Represents a product specification type that defines the structure and attributes available for configuring a product.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductSpecificationTypeOutputRepresentation Properties](./apex_class_ricpq_ProductSpecificationTypeOR.htm.md#apex_ricpq_ProductSpecificationTypeOR_properties)**  

Learn more about the properties available with the     ProductSpecificationTypeOutputRepresentation class.

  

## ProductSpecificationTypeOutputRepresentation Properties

  
  
  
Learn more about the properties available with the
    ProductSpecificationTypeOutputRepresentation class.

    
      

The `ProductSpecificationTypeOutputRepresentation` class
        includes these properties.

    

    
  

- 
**[name](./apex_class_ricpq_ProductSpecificationTypeOR.htm.md#apex_ricpq_ProductSpecificationTypeOR_name)**  

Get or set the name of the product specification type.

- 
**[productSpecificationRecordType](./apex_class_ricpq_ProductSpecificationTypeOR.htm.md#apex_ricpq_ProductSpecificationTypeOR_productSpecificationRecordType)**  

Get or set the product specification record type associated with this specification type.

### name

Get or set the name of the product specification type.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### productSpecificationRecordType

Get or set the product specification record type associated with this specification type.

#### Signature

`public runtime_industries_cpq.ProductSpecificationRecordTypeOutputRepresentation productSpecificationRecordType {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductSpecificationRecordTypeOutputRepresentation
