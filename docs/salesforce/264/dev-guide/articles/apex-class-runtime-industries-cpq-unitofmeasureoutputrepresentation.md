---
page_id: apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation
title: UnitOfMeasureOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm
fetched_at: 2026-11-25
---

# UnitOfMeasureOutputRepresentation Class

Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[UnitOfMeasureOutputRepresentation Constructor](#unitofmeasureoutputrepresentation-constructor)**

Learn more about the constructor that’s available with the UnitOfMeasureOutputRepresentation class.

- 

**[UnitOfMeasureOutputRepresentation Properties](#unitofmeasureoutputrepresentation-properties)**

Contains properties to include unit of measure details for products.

## UnitOfMeasureOutputRepresentation Constructor

Learn more about the constructor that’s available with the UnitOfMeasureOutputRepresentation class.

The `UnitOfMeasureOutputRepresentation` class includes this constructor.

- 

**[UnitOfMeasureOutputRepresentation(apexObj)](#unitofmeasureoutputrepresentationapexobj)**

Constructor to create a UnitOfMeasureOutputRepresentation instance from a ConnectApi UnitOfMeasureOutputRepresentation object.

### UnitOfMeasureOutputRepresentation(apexObj)

Constructor to create a UnitOfMeasureOutputRepresentation instance from a ConnectApi UnitOfMeasureOutputRepresentation object.

#### Signature

`public UnitOfMeasureOutputRepresentation(ConnectApi.UnitOfMeasureOutputRepresentation apexObj)`

#### Parameters

***apexObj***

Type: ConnectApi.UnitOfMeasureOutputRepresentation

The ConnectApi unit of measure representation object to convert to UnitOfMeasureOutputRepresentation.

## UnitOfMeasureOutputRepresentation Properties

Contains properties to include unit of measure details for products.

The `UnitOfMeasureOutputRepresentation` class includes these properties.

- 

**[id](#id)**

Get the ID of the unitofmeasure.

- 

**[name](#name)**

Get the name of the unitofmeasure.

- 

**[roundingMethod](#roundingmethod)**

Get the roundingmethod value.

- 

**[scale](#scale)**

Get the scale value.

- 

**[unitCode](#unitcode)**

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
