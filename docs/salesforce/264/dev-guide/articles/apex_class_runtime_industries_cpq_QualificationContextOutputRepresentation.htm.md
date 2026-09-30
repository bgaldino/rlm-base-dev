---
page_id: apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm
title: QualificationContextOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-09-29
---

# QualificationContextOutputRepresentation Class

Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[QualificationContextOutputRepresentation Properties](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_ricpq_QualificationContextOR_properties)**  

Learn more about the properties available with the     QualificationContextOutputRepresentation class.

  

## QualificationContextOutputRepresentation Properties

  
  
  
Learn more about the properties available with the
    QualificationContextOutputRepresentation class.

    
      

The `QualificationContextOutputRepresentation` class
        includes these properties.

    

    
  

- 
**[isQualified](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_ricpq_QualificationContextOR_isQualified)**  

Get or set whether the product is qualified based on the qualification rules.

- 
**[reason](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_runtime_industries_cpq_QualificationContextOutputRepresentation_reason)**  

Get or set the reason for the qualification result, explaining why the product is qualified or not qualified.

### isQualified

Get or set whether the product is qualified based on the qualification rules.

#### Signature

`public Boolean isQualified {get; set;}`

#### Property Value

Type: Boolean

### reason

Get or set the reason for the qualification result, explaining why the product is qualified or not qualified.

#### Signature

`public String reason {get; set;}`

#### Property Value

Type: String
