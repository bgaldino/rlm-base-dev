---
page_id: apex-class-runtime-industries-cpq-productpricesoutputrepresentation
title: ProductPricesOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productpricesoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductPricesOutputRepresentation Class

Get the price details of a product.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductPricesOutputRepresentation Properties](#productpricesoutputrepresentation-properties)**

Learn more about the properties available with the ProductPricesOutputRepresentation class.

## ProductPricesOutputRepresentation Properties

Learn more about the properties available with the ProductPricesOutputRepresentation class.

The following are properties for `ProductPricesOutputRepresentation`.

- 

**[currencyIsoCode](#currencyisocode)**

Get or set the ISO currency code for the price.

- 

**[effectiveFrom](#effectivefrom)**

Get or set the date and time when this price becomes effective.

- 

**[effectiveTo](#effectiveto)**

Get or set the date and time when this price expires.

- 

**[isDefault](#isdefault)**

Indicates whether this is the default price for the product.

- 

**[isDerived](#isderived)**

Indicates whether this price is derived from another price.

- 

**[isSelected](#isselected)**

Indicates whether this price is currently selected.

- 

**[price](#price)**

Get or set the price value for the product.

- 

**[priceBookEntryId](#pricebookentryid)**

Get or set the ID of the price book entry.

- 

**[priceBookId](#pricebookid)**

Get or set the ID of the price book containing this price.

- 

**[pricingModel](#pricingmodel)**

Get or set the pricing model associated with this price.

### currencyIsoCode

Get or set the ISO currency code for the price.

#### Signature

`public String currencyIsoCode {get; set;}`

#### Property Value

Type: String

### effectiveFrom

Get or set the date and time when this price becomes effective.

#### Signature

`public String effectiveFrom {get; set;}`

#### Property Value

Type: String

### effectiveTo

Get or set the date and time when this price expires.

#### Signature

`public String effectiveTo {get; set;}`

#### Property Value

Type: String

### isDefault

Indicates whether this is the default price for the product.

#### Signature

`public Boolean isDefault {get; set;}`

#### Property Value

Type: Boolean

### isDerived

Indicates whether this price is derived from another price.

#### Signature

`public Boolean isDerived {get; set;}`

#### Property Value

Type: Boolean

### isSelected

Indicates whether this price is currently selected.

#### Signature

`public Boolean isSelected {get; set;}`

#### Property Value

Type: Boolean

### price

Get or set the price value for the product.

#### Signature

`public Double price {get; set;}`

#### Property Value

Type: Double

### priceBookEntryId

Get or set the ID of the price book entry.

#### Signature

`public String priceBookEntryId {get; set;}`

#### Property Value

Type: String

### priceBookId

Get or set the ID of the price book containing this price.

#### Signature

`public String priceBookId {get; set;}`

#### Property Value

Type: String

### pricingModel

Get or set the pricing model associated with this price.

#### Signature

`public runtime_industries_cpq.PricingModelOutputRepresentation pricingModel {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.PricingModelOutputRepresentation](./apex-class-runtime-industries-cpq-pricingmodeloutputrepresentation.md#pricingmodeloutputrepresentation-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productpricesoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
