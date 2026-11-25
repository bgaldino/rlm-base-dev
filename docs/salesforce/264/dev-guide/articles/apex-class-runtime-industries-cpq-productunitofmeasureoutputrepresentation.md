---
page_id: apex-class-runtime-industries-cpq-productunitofmeasureoutputrepresentation
title: ProductUnitOfMeasureOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productunitofmeasureoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductUnitOfMeasureOutputRepresentation Class

Represents a unit of measure that’s available for a product, including whether it’s the base or default unit and whether it’s orderable.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductUnitOfMeasureOutputRepresentation Constructor](#productunitofmeasureoutputrepresentation-constructor)**

Learn more about the constructor that’s available with the ProductUnitOfMeasureOutputRepresentation class.

- 

**[ProductUnitOfMeasureOutputRepresentation Properties](#productunitofmeasureoutputrepresentation-properties)**

Contains properties to include unit of measure details for products.

## ProductUnitOfMeasureOutputRepresentation Constructor

Learn more about the constructor that’s available with the ProductUnitOfMeasureOutputRepresentation class.

The `ProductUnitOfMeasureOutputRepresentation` class includes this constructor.

- 

**[ProductUnitOfMeasureOutputRepresentation(apexObj)](#productunitofmeasureoutputrepresentationapexobj)**

Constructor to create a ProductUnitOfMeasureOutputRepresentation instance from a ConnectApi.CPQProductUnitOfMeasureOutputRepresentation object.

### ProductUnitOfMeasureOutputRepresentation(apexObj)

Constructor to create a ProductUnitOfMeasureOutputRepresentation instance from a ConnectApi.CPQProductUnitOfMeasureOutputRepresentation object.

#### Signature

`public ProductUnitOfMeasureOutputRepresentation(ConnectApi.CPQProductUnitOfMeasureOutputRepresentation apexObj)`

#### Parameters

***apexObj***

: 

Type: ConnectApi.CPQProductUnitOfMeasureOutputRepresentation

The ConnectApi CPQProductUnitOfMeasureOutputRepresentation object to convert to ProductUnitOfMeasureOutputRepresentation.

## ProductUnitOfMeasureOutputRepresentation Properties

Contains properties to include unit of measure details for products.

The `ProductUnitOfMeasureOutputRepresentation` class includes these properties.

- 

**[id](#id)**

Get the ID of the product unit of measure.

- 

**[isBaseUnit](#isbaseunit)**

Get whether the unit of measure is the base unit of measure for the product.

- 

**[isDefaultUnit](#isdefaultunit)**

Get whether the unit of measure is the default unit of measure for the product.

- 

**[isOrderable](#isorderable)**

Get whether the product can be ordered in this unit of measure.

- 

**[sequence](#sequence)**

Get the sequence of the unit of measure.

- 

**[unitOfMeasureInfo](#unitofmeasureinfo)**

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

Type: [runtime_industries_cpq.UnitOfMeasureOutputRepresentation](./apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation.md#unitofmeasureoutputrepresentation-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productunitofmeasureoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
