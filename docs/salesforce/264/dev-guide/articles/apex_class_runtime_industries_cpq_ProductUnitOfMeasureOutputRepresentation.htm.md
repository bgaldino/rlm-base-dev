---
page_id: apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm
title: ProductUnitOfMeasureOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-09-29
---

# ProductUnitOfMeasureOutputRepresentation Class

Represents a unit of measure that's available for a product, including whether it's the base or default unit and whether it's orderable.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductUnitOfMeasureOutputRepresentation Constructor](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_constructors)**  

Learn more about the constructor that's available with the ProductUnitOfMeasureOutputRepresentation class.

- 
**[ProductUnitOfMeasureOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_properties)**  

Contains properties to include unit of measure details for products.

  

## ProductUnitOfMeasureOutputRepresentation Constructor

  
  
  
Learn more about the constructor that's available with the ProductUnitOfMeasureOutputRepresentation class.

    
      

The `ProductUnitOfMeasureOutputRepresentation` class includes this constructor.

    

    
  

- 
**[ProductUnitOfMeasureOutputRepresentation(apexObj)](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_ctor)**  

Constructor to create a ProductUnitOfMeasureOutputRepresentation instance from a ConnectApi.CPQProductUnitOfMeasureOutputRepresentation object.

### ProductUnitOfMeasureOutputRepresentation(apexObj)

Constructor to create a ProductUnitOfMeasureOutputRepresentation instance from a ConnectApi.CPQProductUnitOfMeasureOutputRepresentation object.

#### Signature

`public ProductUnitOfMeasureOutputRepresentation(ConnectApi.CPQProductUnitOfMeasureOutputRepresentation apexObj)`

#### Parameters

**apexObj**

: Type: ConnectApi.CPQProductUnitOfMeasureOutputRepresentation

: The ConnectApi CPQProductUnitOfMeasureOutputRepresentation object to convert to ProductUnitOfMeasureOutputRepresentation.

  

## ProductUnitOfMeasureOutputRepresentation Properties

  
  
  
Contains properties to include unit of measure details for products.

    
      

The `ProductUnitOfMeasureOutputRepresentation` class includes these
        properties.

    

    
  

- 
**[id](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_id)**  

Get the ID of the product unit of measure.

- 
**[isBaseUnit](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_isBaseUnit)**  

Get whether the unit of measure is the base unit of measure for the product.

- 
**[isDefaultUnit](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_isDefaultUnit)**  

Get whether the unit of measure is the default unit of measure for the product.

- 
**[isOrderable](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_isOrderable)**  

Get whether the product can be ordered in this unit of measure.

- 
**[sequence](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_sequence)**  

Get the sequence of the unit of measure.

- 
**[unitOfMeasureInfo](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation_unitOfMeasureInfo)**  

Get the details of the unit of measure.

### id

Get the ID of the product unit of measure.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isBaseUnit

Get whether the unit of measure is the base unit of measure for the product.

#### Signature

`public Boolean isBaseUnit {get; set;}`

#### Property Value

Type: Boolean

### isDefaultUnit

Get whether the unit of measure is the default unit of measure for the product.

#### Signature

`public Boolean isDefaultUnit {get; set;}`

#### Property Value

Type: Boolean

### isOrderable

Get whether the product can be ordered in this unit of measure.

#### Signature

`public Boolean isOrderable {get; set;}`

#### Property Value

Type: Boolean

### sequence

Get the sequence of the unit of measure.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

### unitOfMeasureInfo

Get the details of the unit of measure.

#### Signature

`public runtime_industries_cpq.UnitOfMeasureOutputRepresentation unitOfMeasureInfo {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.UnitOfMeasureOutputRepresentation](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation)
