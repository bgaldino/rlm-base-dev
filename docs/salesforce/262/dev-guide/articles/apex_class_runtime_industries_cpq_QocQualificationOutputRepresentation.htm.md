---
page_id: apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm
title: QocQualificationOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# QocQualificationOutputRepresentation Class

Represents a quote, order, or contract qualification that determines whether a product
can be sold based on specific business rules and conditions.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[QocQualificationOutputRepresentation Constructors](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_constructors)**
- **[QocQualificationOutputRepresentation Properties](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_properties)**  
  Learn more about the properties available with the QocQualificationOutputRepresentation class.

## QocQualificationOutputRepresentation Constructors

The following are constructors for `QocQualificationOutputRepresentation`.

- **[QocQualificationOutputRepresentation()](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_ctor_2)**  
  Constructs an empty QocQualificationOutputRepresentation instance.

### QocQualificationOutputRepresentation()

Constructs an empty QocQualificationOutputRepresentation instance.

#### Signature

`public QocQualificationOutputRepresentation()`

## QocQualificationOutputRepresentation Properties

Learn more about the properties available with the QocQualificationOutputRepresentation
class.

The `QocQualificationOutputRepresentation` class includes
these properties.

- **[productId](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_productId)**  
  Get or set the identifier of the product being qualified.
- **[qualificationContext](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_qualificationContext)**  
  Get or set the qualification context that contains the qualification result and reason.

### productId

Get or set the identifier of the product being qualified.

#### Signature

`public String productId {get; set;}`

#### Property Value

Type: String

### qualificationContext

Get or set the qualification context that contains the qualification result and reason.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: runtime\_industries\_cpq.QualificationContextOutputRepresentation
