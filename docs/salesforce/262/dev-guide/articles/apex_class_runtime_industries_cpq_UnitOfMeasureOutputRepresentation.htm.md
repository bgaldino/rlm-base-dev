---
page_id: apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm
title: UnitOfMeasureOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# UnitOfMeasureOutputRepresentation Class

Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[UnitOfMeasureOutputRepresentation Constructor](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_constructors)**  
  Learn more about the constructor that's available with the UnitOfMeasureOutputRepresentation class.
- **[UnitOfMeasureOutputRepresentation Properties](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_properties)**  
  Contains properties to include unit of measure details for products.

## UnitOfMeasureOutputRepresentation Constructor

Learn more about the constructor that's available with the UnitOfMeasureOutputRepresentation
class.

The `UnitOfMeasureOutputRepresentation` class includes this
constructor.

- **[UnitOfMeasureOutputRepresentation(apexObj)](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_ctor)**  
  Constructor to create a UnitOfMeasureOutputRepresentation instance from a ConnectApi UnitOfMeasureOutputRepresentation object.

### UnitOfMeasureOutputRepresentation(apexObj)

Constructor to create a UnitOfMeasureOutputRepresentation instance from a ConnectApi UnitOfMeasureOutputRepresentation object.

#### Signature

`public UnitOfMeasureOutputRepresentation(ConnectApi.UnitOfMeasureOutputRepresentation apexObj)`

#### Parameters

apexObj
:   Type: ConnectApi.UnitOfMeasureOutputRepresentation
:   The ConnectApi unit of measure representation object to convert to UnitOfMeasureOutputRepresentation.

## UnitOfMeasureOutputRepresentation Properties

Contains properties to include unit of measure details for products.

The `UnitOfMeasureOutputRepresentation` class includes these
properties.

- **[id](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_id)**  
  Get the ID of the unitofmeasure.
- **[name](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_name)**  
  Get the name of the unitofmeasure.
- **[roundingMethod](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_roundingMethod)**  
  Get the roundingmethod value.
- **[scale](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_scale)**  
  Get the scale value.
- **[unitCode](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_runtime_industries_cpq_UnitOfMeasureOutputRepresentation_unitCode)**  
  Get the unitcode value.

### id

Get the ID of the unitofmeasure.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the unitofmeasure.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### roundingMethod

Get the roundingmethod value.

#### Signature

`public String roundingMethod {get; set;}`

#### Property Value

Type: String

### scale

Get the scale value.

#### Signature

`public Integer scale {get; set;}`

#### Property Value

Type: Integer

### unitCode

Get the unitcode value.

#### Signature

`public String unitCode {get; set;}`

#### Property Value

Type: String
