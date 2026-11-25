---
page_id: apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation
title: AttributeCategoryOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm
fetched_at: 2026-11-25
---

# AttributeCategoryOutputRepresentation Class

Stores details of an attribute such as code, description, usage type, and so on.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[AttributeCategoryOutputRepresentation Properties](#attributecategoryoutputrepresentation-properties)**

Contains properties to include details of an attribute.

## AttributeCategoryOutputRepresentation Properties

Contains properties to include details of an attribute.

The `AttributeCategoryOutputRepresentation` class includes these properties.

- 

**[code](#code)**

Get the code of the attribute category.

- 

**[description](#description)**

Get the description of the attribute category.

- 

**[id](#id)**

Get the ID of the attribute category.

- 

**[name](#name)**

Get the name of the attribute category.

- 

**[records](#records)**

Get the attributes of the attribute category.

- 

**[sequence](#sequence)**

Get the sequence of the attribute category.

- 

**[status](#status)**

Get the status of the attribute category.

- 

**[totalSize](#totalsize)**

Get the total size of the attribute category.

- 

**[usageType](#usagetype)**

Get the usage type of the attribute category.

### code

Get the code of the attribute category.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### description

Get the description of the attribute category.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the attribute category.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the attribute category.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### records

Get the attributes of the attribute category.

#### Signature

`public List<runtime_industries_cpq.ProductAttributeOutputRepresentation> records {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductAttributeOutputRepresentation](./apex-class-runtime-industries-cpq-productattributeoutputrepresentation.md#productattributeoutputrepresentation-class)>

### sequence

Get the sequence of the attribute category.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

### status

Get the status of the attribute category.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### totalSize

Get the total size of the attribute category.

#### Signature

`public Integer totalSize {get; set;}`

#### Property Value

Type: Integer

### usageType

Get the usage type of the attribute category.

#### Signature

`public String usageType {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
