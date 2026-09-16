---
page_id: apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm
title: RelatedObjectFilterInputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# RelatedObjectFilterInputRepresentation Class

Represents input criteria for filtering products based on related object information, such as account, opportunity, or contract data.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[RelatedObjectFilterInputRepresentation Properties](./apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm.md#apex_ricpq_RelatedObjectFilterIR_properties)**  

Learn more about the properties available with the     RelatedObjectFilterInputRepresentation

  

## RelatedObjectFilterInputRepresentation Properties

  
  
  
Learn more about the properties available with the
    RelatedObjectFilterInputRepresentation

    
      

The `RelatedObjectFilterInputRepresentation` class
        includes these properties.

    

    
  

- 
**[relatedObjectFilter](./apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm.md#apex_ricpq_RelatedObjectFilterIR_relatedObjectFilter)**  

Get or set the list of related object filters to apply when searching for products.

### relatedObjectFilter

Get or set the list of related object filters to apply when searching for products.

#### Signature

`public List<runtime_industries_cpq.RelatedObjectFilter> relatedObjectFilter {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.RelatedObjectFilter>
