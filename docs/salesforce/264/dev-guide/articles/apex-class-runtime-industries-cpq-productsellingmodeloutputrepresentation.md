---
page_id: apex-class-runtime-industries-cpq-productsellingmodeloutputrepresentation
title: ProductSellingModelOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productsellingmodeloutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductSellingModelOutputRepresentation Class

Represents a product selling model that defines how a product is sold, including the selling model type, pricing term, and status.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductSellingModelOutputRepresentation Properties](#productsellingmodeloutputrepresentation-properties)**

Learn more about the properties available with the ProductSellingModelOutputRepresentation class.

## ProductSellingModelOutputRepresentation Properties

Learn more about the properties available with the ProductSellingModelOutputRepresentation class.

The `ProductSellingModelOutputRepresentation` class includes these properties.

- 

**[id](#id)**

Get or set the unique identifier of the product selling model.

- 

**[name](#name)**

Get or set the name of the product selling model.

- 

**[pricingTerm](#pricingterm)**

Get or set the pricing term value, which represents the duration or quantity for the pricing term unit.

- 

**[pricingTermUnit](#pricingtermunit)**

Get or set the unit for the pricing term, such as “Month”, “Year”, or “Day”.

- 

**[sellingModelType](#sellingmodeltype)**

Get or set the type of selling model, such as “Subscription”, “OneTime”, or “Usage”.

- 

**[status](#status)**

Get or set the status of the product selling model, such as “Active” or “Inactive”.

### id

Get or set the unique identifier of the product selling model.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get or set the name of the product selling model.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### pricingTerm

Get or set the pricing term value, which represents the duration or quantity for the pricing term unit.

#### Signature

`public Integer pricingTerm {get; set;}`

#### Property Value

Type: Integer

### pricingTermUnit

Get or set the unit for the pricing term, such as “Month”, “Year”, or “Day”.

#### Signature

`public String pricingTermUnit {get; set;}`

#### Property Value

Type: String

### sellingModelType

Get or set the type of selling model, such as “Subscription”, “OneTime”, or “Usage”.

#### Signature

`public String sellingModelType {get; set;}`

#### Property Value

Type: String

### status

Get or set the status of the product selling model, such as “Active” or “Inactive”.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productsellingmodeloutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
