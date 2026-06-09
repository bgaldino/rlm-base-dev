---
page_id: apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm
title: ProductSpecificationTypeOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductSpecificationTypeOutputRepresentation Class

Represents a product specification type that defines the structure and attributes available for configuring a product.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductSpecificationTypeOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductSpecificationTypeOutputRepresentation class.

## ProductSpecificationTypeOutputRepresentation Properties

Learn more about the properties available with the
ProductSpecificationTypeOutputRepresentation class.

The `ProductSpecificationTypeOutputRepresentation` class
includes these properties.

- **[name](./apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation_name)**  
  Get or set the name of the product specification type.
- **[productSpecificationRecordType](./apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation_productSpecificationRecordType)**  
  Get or set the product specification record type associated with this specification type.

### name

Get or set the name of the product specification type.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### productSpecificationRecordType

Get or set the product specification record type associated with this specification type.

#### Signature

`public runtime_industries_cpq.ProductSpecificationRecordTypeOutputRepresentation productSpecificationRecordType {get; set;}`

#### Property Value

Type: runtime\_industries\_cpq.ProductSpecificationRecordTypeOutputRepresentation
