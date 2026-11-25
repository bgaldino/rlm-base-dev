---
page_id: apex-class-ricpq-productsellingmodeloptionor
title: ProductSellingModelOptionOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-ricpq-productsellingmodeloptionor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_ricpq_ProductSellingModelOptionOR.htm
fetched_at: 2026-11-25
---

# ProductSellingModelOptionOutputRepresentation Class

Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductSellingModelOptionOutputRepresentation Properties](#productsellingmodeloptionoutputrepresentation-properties)**

Learn more about the properties available with the ProductSellingModelOptionOutputRepresentation class.

## ProductSellingModelOptionOutputRepresentation Properties

Learn more about the properties available with the ProductSellingModelOptionOutputRepresentation class.

The `ProductSellingModelOptionOutputRepresentation` class includes these properties.

- 

**[id](#id)**

Get or set the unique identifier of the product selling model option.

- 

**[productId](#productid)**

Get or set the identifier of the product that this selling model option applies to.

- 

**[productSellingModel](#productsellingmodel)**

Get or set the product selling model details for this option.

- 

**[productSellingModelId](#productsellingmodelid)**

Get or set the identifier of the product selling model for this option.

### id

Get or set the unique identifier of the product selling model option.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### productId

Get or set the identifier of the product that this selling model option applies to.

#### Signature

`public String productId {get; set;}`

#### Property Value

Type: String

### productSellingModel

Get or set the product selling model details for this option.

#### Signature

`public runtime_industries_cpq.ProductSellingModelOutputRepresentation productSellingModel {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductSellingModelOutputRepresentation

### productSellingModelId

Get or set the identifier of the product selling model for this option.

#### Signature

`public String productSellingModelId {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-ricpq-productsellingmodeloptionor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
