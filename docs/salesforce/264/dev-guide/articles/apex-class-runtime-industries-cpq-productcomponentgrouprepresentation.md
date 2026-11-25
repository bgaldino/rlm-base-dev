---
page_id: apex-class-runtime-industries-cpq-productcomponentgrouprepresentation
title: ProductComponentGroupRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productcomponentgrouprepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm
fetched_at: 2026-11-25
---

# ProductComponentGroupRepresentation Class

Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductComponentGroupRepresentation Constructor](#productcomponentgrouprepresentation-constructor)**

Learn more about the constructor that’s available with the ProductComponentGroupRepresentation class.

- 

**[ProductComponentGroupRepresentation Properties](#productcomponentgrouprepresentation-properties)**

Contains properties to include details of a product component group used in bulk operations.

## ProductComponentGroupRepresentation Constructor

Learn more about the constructor that’s available with the ProductComponentGroupRepresentation class.

The `ProductComponentGroupRepresentation` class includes this constructor.

- 

**[ProductComponentGroupRepresentation(apexObj)](#productcomponentgrouprepresentationapexobj)**

Constructor to create a ProductComponentGroupRepresentation instance from a ConnectApi CPQProductComponentGroupOutputRepresentation object.

### ProductComponentGroupRepresentation(apexObj)

Constructor to create a ProductComponentGroupRepresentation instance from a ConnectApi CPQProductComponentGroupOutputRepresentation object.

#### Signature

`public ProductComponentGroupRepresentation(ConnectApi.CPQProductComponentGroupOutputRepresentation apexObj)`

#### Parameters

***apexObj***

Type: ConnectApi.CPQProductComponentGroupOutputRepresentation

The ConnectApi product component group representation object to convert to ProductComponentGroupRepresentation.

## ProductComponentGroupRepresentation Properties

Contains properties to include details of a product component group used in bulk operations.

The `ProductComponentGroupRepresentation` class includes these properties.

- 

**[childGroups](#childgroups)**

Get the list of childgroup.

- 

**[classifications](#classifications)**

Get the list of product classifications.

- 

**[code](#code)**

Get the code of the productcomponentgroup.

- 

**[components](#components)**

Get the list of component.

- 

**[description](#description)**

Get the description of the productcomponentgroup.

- 

**[id](#id)**

Get the ID of the productcomponentgroup.

- 

**[name](#name)**

Get the name of the productcomponentgroup.

- 

**[parentGroupId](#parentgroupid)**

Get the ID of the parentgroup.

- 

**[parentProductId](#parentproductid)**

Get the ID of the parentproduct.

- 

**[sequence](#sequence)**

Get the sequence value.

### childGroups

Get the list of childgroup.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupRepresentation> childGroups {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductComponentGroupRepresentation](#productcomponentgrouprepresentation-class)>

### classifications

Get the list of product classifications.

#### Signature

`public List<runtime_industries_cpq.ProductClassificationOutputRepresentation> classifications {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductClassificationOutputRepresentation](./apex-class-runtime-industries-cpq-productclassificationoutputrepresentation.md#productclassificationoutputrepresentation-class)>

### code

Get the code of the productcomponentgroup.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### components

Get the list of component.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsRepresentation> components {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.BulkProductDetailsRepresentation](./apex-class-runtime-industries-cpq-bulkproductdetailsrepresentation.md#bulkproductdetailsrepresentation-class)>

### description

Get the description of the productcomponentgroup.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the productcomponentgroup.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the productcomponentgroup.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### parentGroupId

Get the ID of the parentgroup.

#### Signature

`public String parentGroupId {get; set;}`

#### Property Value

Type: String

### parentProductId

Get the ID of the parentproduct.

#### Signature

`public String parentProductId {get; set;}`

#### Property Value

Type: String

### sequence

Get the sequence value.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productcomponentgrouprepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
