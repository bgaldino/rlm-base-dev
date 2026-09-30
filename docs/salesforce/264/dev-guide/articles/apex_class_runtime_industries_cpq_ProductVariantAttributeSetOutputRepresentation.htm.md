---
page_id: apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm
title: ProductVariantAttributeSetOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-09-29
---

# ProductVariantAttributeSetOutputRepresentation Class

Stores the set of attributes that define the variations of a product.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductVariantAttributeSetOutputRepresentation Constructors](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_constructors)**  

- 
**[ProductVariantAttributeSetOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_properties)**  

Contains properties of the ProductVariantAttributeSetOutputRepresentation class.

  

## ProductVariantAttributeSetOutputRepresentation Constructors

  
  
    
      

The following are constructors for `ProductVariantAttributeSetOutputRepresentation`.

    

    
  

- 
**[ProductVariantAttributeSetOutputRepresentation()](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_ctor_2)**  

Constructor to create a ProductVariantAttributeSetOutputRepresentation instance.

### ProductVariantAttributeSetOutputRepresentation()

Constructor to create a ProductVariantAttributeSetOutputRepresentation instance.

#### Signature

`public ProductVariantAttributeSetOutputRepresentation()`

  

## ProductVariantAttributeSetOutputRepresentation Properties

  
  
  
Contains properties of the ProductVariantAttributeSetOutputRepresentation class.

    
      

The `ProductVariantAttributeSetOutputRepresentation` class includes
        these properties.

    

    
  

- 
**[attributes](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_attributes)**  

Get the map of variation attribute values, where the key is the attribute name and the value is the attribute value.

- 
**[description](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_description)**  

Get the description of the variation attribute set.

- 
**[developerName](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_developerName)**  

Get the developer name of the variation attribute set.

- 
**[id](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_id)**  

Get the ID of the variation attribute set.

- 
**[label](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation_label)**  

Get the label of the variation attribute set.

### attributes

Get the map of variation attribute values, where the key is the attribute name and the value is the attribute value.

#### Signature

`public Map<String,runtime_industries_cpq.ProductVariantAttributeValueOutputRepresentation> attributes {get; set;}`

#### Property Value

Type: Map<String,[runtime_industries_cpq.ProductVariantAttributeValueOutputRepresentation](./apex_class_runtime_industries_cpq_ProductVariantAttributeValueOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductVariantAttributeValueOutputRepresentation)>

### description

Get the description of the variation attribute set.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### developerName

Get the developer name of the variation attribute set.

#### Signature

`public String developerName {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the variation attribute set.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### label

Get the label of the variation attribute set.

#### Signature

`public String label {get; set;}`

#### Property Value

Type: String
