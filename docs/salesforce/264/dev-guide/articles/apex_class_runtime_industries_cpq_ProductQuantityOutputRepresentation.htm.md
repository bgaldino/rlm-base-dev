---
page_id: apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm
title: ProductQuantityOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductQuantityOutputRepresentation Class

Represents the quantity constraints and current quantity for a product in the product discovery context.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductQuantityOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_properties)**  

## ProductQuantityOutputRepresentation Properties

The following are properties for `ProductQuantityOutputRepresentation`.

- 
**[maxQuantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_maxQuantity)**  

Get or set the maximum quantity allowed for the product.

- 
**[minQuantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_minQuantity)**  

Get or set the minimum quantity allowed for the product.

- 
**[quantity](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductQuantityOutputRepresentation_quantity)**  

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
