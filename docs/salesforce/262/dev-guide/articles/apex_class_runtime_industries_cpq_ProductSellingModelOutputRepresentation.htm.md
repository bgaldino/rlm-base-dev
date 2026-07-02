---
page_id: apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm
title: ProductSellingModelOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductSellingModelOutputRepresentation Class

Represents a product selling model that defines how a product is sold, including the selling model type, pricing term, and status.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductSellingModelOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductSellingModelOutputRepresentation class.

## ProductSellingModelOutputRepresentation Properties

Learn more about the properties available with the
ProductSellingModelOutputRepresentation class.

The `ProductSellingModelOutputRepresentation` class
includes these properties.

- **[id](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_id)**  
  Get or set the unique identifier of the product selling model.
- **[name](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_name)**  
  Get or set the name of the product selling model.
- **[pricingTerm](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_pricingTerm)**  
  Get or set the pricing term value, which represents the duration or quantity for the pricing term unit.
- **[pricingTermUnit](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_pricingTermUnit)**  
  Get or set the unit for the pricing term, such as "Month", "Year", or "Day".
- **[sellingModelType](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_sellingModelType)**  
  Get or set the type of selling model, such as "Subscription", "OneTime", or "Usage".
- **[status](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOutputRepresentation_status)**  
  Get or set the status of the product selling model, such as "Active" or "Inactive".

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

Get or set the unit for the pricing term, such as "Month", "Year", or "Day".

#### Signature

`public String pricingTermUnit {get; set;}`

#### Property Value

Type: String

### sellingModelType

Get or set the type of selling model, such as "Subscription", "OneTime", or "Usage".

#### Signature

`public String sellingModelType {get; set;}`

#### Property Value

Type: String

### status

Get or set the status of the product selling model, such as "Active" or "Inactive".

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String
