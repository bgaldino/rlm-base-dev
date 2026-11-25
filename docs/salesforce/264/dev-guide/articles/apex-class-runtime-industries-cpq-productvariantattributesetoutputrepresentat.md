---
page_id: apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat
title: ProductVariantAttributeSetOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductVariantAttributeSetOutputRepresentation Class

Stores the set of attributes that define the variations of a product.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductVariantAttributeSetOutputRepresentation Constructors](#productvariantattributesetoutputrepresentation-constructors)**

- 

**[ProductVariantAttributeSetOutputRepresentation Properties](#productvariantattributesetoutputrepresentation-properties)**

Contains properties of the ProductVariantAttributeSetOutputRepresentation class.

## ProductVariantAttributeSetOutputRepresentation Constructors

The following are constructors for `ProductVariantAttributeSetOutputRepresentation`.

- 

**[ProductVariantAttributeSetOutputRepresentation()](#productvariantattributesetoutputrepresentation)**

Constructor to create a ProductVariantAttributeSetOutputRepresentation instance.

### ProductVariantAttributeSetOutputRepresentation()

Constructor to create a ProductVariantAttributeSetOutputRepresentation instance.

#### Signature

`public ProductVariantAttributeSetOutputRepresentation()`

## ProductVariantAttributeSetOutputRepresentation Properties

Contains properties of the ProductVariantAttributeSetOutputRepresentation class.

The `ProductVariantAttributeSetOutputRepresentation` class includes these properties.

- 

**[attributes](#attributes)**

Get the map of variation attribute values, where the key is the attribute name and the value is the attribute value.

- 

**[description](#description)**

Get the description of the variation attribute set.

- 

**[developerName](#developername)**

Get the developer name of the variation attribute set.

- 

**[id](#id)**

Get the ID of the variation attribute set.

- 

**[label](#label)**

Get the label of the variation attribute set.

### attributes

Get the map of variation attribute values, where the key is the attribute name and the value is the attribute value.

#### Signature

`public Map<String,runtime_industries_cpq.ProductVariantAttributeValueOutputRepresentation> attributes {get; set;}`

#### Property Value

Type: Map<String,[runtime_industries_cpq.ProductVariantAttributeValueOutputRepresentation](./apex-class-runtime-industries-cpq-productvariantattributevalueoutputrepresent.md#productvariantattributevalueoutputrepresentation-class)>

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
