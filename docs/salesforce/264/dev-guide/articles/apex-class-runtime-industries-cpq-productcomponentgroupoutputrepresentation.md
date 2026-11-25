---
page_id: apex-class-runtime-industries-cpq-productcomponentgroupoutputrepresentation
title: ProductComponentGroupOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productcomponentgroupoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductComponentGroupOutputRepresentation Class

Get details of the product component group in a product classification.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductComponentGroupOutputRepresentation Properties](#productcomponentgroupoutputrepresentation-properties)**

Learn more about the properties available with the ProductComponentGroupOutputRepresentation class.

## ProductComponentGroupOutputRepresentation Properties

Learn more about the properties available with the ProductComponentGroupOutputRepresentation class.

The `ProductComponentGroupOutputRepresentation` class includes these properties.

- 

**[childGroups](#childgroups)**

Get the child groups associated with a product component group.

- 

**[classifications](#classifications)**

Get the list of classifications for the product component group.

- 

**[code](#code)**

Get the code of the product component group.

- 

**[components](#components)**

Get the details of components within the product component group.

- 

**[description](#description)**

Get the description of the product component group.

- 

**[id](#id)**

Get the ID of the product component group.

- 

**[name](#name)**

Get the name of the product component group.

- 

**[parentGroupId](#parentgroupid)**

Get the ID of the parent group.

- 

**[parentProductId](#parentproductid)**

Get the parent Product2 ID of the product component group.

- 

**[sequence](#sequence)**

Get the sequence of the product component group.

### childGroups

Get the child groups associated with a product component group.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation> childGroups {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductComponentGroupOutputRepresentation](#productcomponentgroupoutputrepresentation-class)>

### classifications

Get the list of classifications for the product component group.

#### Signature

`public List<runtime_industries_cpq.ProductClassificationOutputRepresentation> classifications {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductClassificationOutputRepresentation](./apex-class-runtime-industries-cpq-productclassificationoutputrepresentation.md#productclassificationoutputrepresentation-class)>

### code

Get the code of the product component group.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### components

Get the details of components within the product component group.

#### Signature

`public List<runtime_industries_cpq.ProductDetailsRepresentation> components {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductDetailsRepresentation](./apex-class-runtime-industries-cpq-productdetailsrepresentation.md#productdetailsrepresentation-class)>

### description

Get the description of the product component group.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the product component group.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the product component group.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### parentGroupId

Get the ID of the parent group.

#### Signature

`public String parentGroupId {get; set;}`

#### Property Value

Type: String

### parentProductId

Get the parent Product2 ID of the product component group.

#### Signature

`public String parentProductId {get; set;}`

#### Property Value

Type: String

### sequence

Get the sequence of the product component group.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productcomponentgroupoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
