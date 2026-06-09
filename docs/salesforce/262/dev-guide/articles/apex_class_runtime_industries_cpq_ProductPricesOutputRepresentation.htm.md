---
page_id: apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm
title: ProductPricesOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductPricesOutputRepresentation Class

Get the price details of a product.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductPricesOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductPricesOutputRepresentation class.

## ProductPricesOutputRepresentation Properties

Learn more about the properties available with the ProductPricesOutputRepresentation
class.

The following are properties for `ProductPricesOutputRepresentation`.

- **[currencyIsoCode](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_currencyIsoCode)**  
  Get or set the ISO currency code for the price.
- **[effectiveFrom](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_effectiveFrom)**  
  Get or set the date and time when this price becomes effective.
- **[effectiveTo](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_effectiveTo)**  
  Get or set the date and time when this price expires.
- **[isDefault](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_isDefault)**  
  Indicates whether this is the default price for the product.
- **[isDerived](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_isDerived)**  
  Indicates whether this price is derived from another price.
- **[isSelected](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_isSelected)**  
  Indicates whether this price is currently selected.
- **[price](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_price)**  
  Get or set the price value for the product.
- **[priceBookEntryId](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_priceBookEntryId)**  
  Get or set the ID of the price book entry.
- **[priceBookId](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_priceBookId)**  
  Get or set the ID of the price book containing this price.
- **[pricingModel](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductPricesOutputRepresentation_pricingModel)**  
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

Type: [runtime\_industries\_cpq.PricingModelOutputRepresentation](./apex_class_runtime_industries_cpq_PricingModelOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_PricingModelOutputRepresentation "Contains details of a pricing model in a product configuration.")
