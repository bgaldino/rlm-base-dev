---
page_id: apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm
title: ProductSellingModelOptionOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductSellingModelOptionOutputRepresentation Class

Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductSellingModelOptionOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductSellingModelOptionOutputRepresentation class.

## ProductSellingModelOptionOutputRepresentation Properties

Learn more about the properties available with the
ProductSellingModelOptionOutputRepresentation class.

The `ProductSellingModelOptionOutputRepresentation` class
includes these properties.

- **[id](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_id)**  
  Get or set the unique identifier of the product selling model option.
- **[productId](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_productId)**  
  Get or set the identifier of the product that this selling model option applies to.
- **[productSellingModel](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_productSellingModel)**  
  Get or set the product selling model details for this option.
- **[productSellingModelId](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation_productSellingModelId)**  
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

Type: runtime\_industries\_cpq.ProductSellingModelOutputRepresentation

### productSellingModelId

Get or set the identifier of the product selling model for this option.

#### Signature

`public String productSellingModelId {get; set;}`

#### Property Value

Type: String
