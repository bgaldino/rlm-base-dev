---
page_id: apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm
title: QocQualificationOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# QocQualificationOutputRepresentation Class

Represents a quote, order, or contract qualification that determines whether a product
    can be sold based on specific business rules and conditions.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[QocQualificationOutputRepresentation Constructors](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_ricpq_QocQualificationOR_constructors)**  

- 
**[QocQualificationOutputRepresentation Properties](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_properties)**  

Learn more about the properties available with the QocQualificationOutputRepresentation     class.

## QocQualificationOutputRepresentation Constructors

The following are constructors for `QocQualificationOutputRepresentation`.

- 
**[QocQualificationOutputRepresentation()](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_ctor_2)**  

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

    

    
  

- 
**[productId](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_runtime_industries_cpq_QocQualificationOutputRepresentation_productId)**  

Get or set the identifier of the product being qualified.

- 
**[qualificationContext](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md#apex_ricpq_QocQualificationOR_qualificationContext)**  

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

Type: runtime_industries_cpq.QualificationContextOutputRepresentation
