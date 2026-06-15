---
page_id: apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm
title: ProductQuantityOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductQuantityOutputRepresentation Class

Represents the quantity constraints and current quantity for a product in the product discovery context.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductQuantityOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_properties)**

## ProductQuantityOutputRepresentation Properties

The following are properties for `ProductQuantityOutputRepresentation`.

- **[maxQuantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_maxQuantity)**  
  Get or set the maximum quantity allowed for the product.
- **[minQuantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_minQuantity)**  
  Get or set the minimum quantity allowed for the product.
- **[quantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_quantity)**  
  Get or set the current quantity of the product.

### maxQuantity

Get or set the maximum quantity allowed for the product.

#### Signature

`public Double maxQuantity {get; set;}`

#### Property Value

Type: Double

### minQuantity

Get or set the minimum quantity allowed for the product.

#### Signature

`public Double minQuantity {get; set;}`

#### Property Value

Type: Double

### quantity

Get or set the current quantity of the product.

#### Signature

`public Double quantity {get; set;}`

#### Property Value

Type: Double
