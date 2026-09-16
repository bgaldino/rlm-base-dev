---
page_id: apex_class_runtime_industries_cpq_RelatedObjectFilter.htm
title: RelatedObjectFilter Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_RelatedObjectFilter.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# RelatedObjectFilter Class

Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[RelatedObjectFilter Properties](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_properties)**  

Learn more about the properties available with the RelatedObjectFilter     class.

  

## RelatedObjectFilter Properties

  
  
  
Learn more about the properties available with the RelatedObjectFilter
    class.

    
      

The `RelatedObjectFilter` class includes these
        properties.

    

    
  

- 
**[criteria](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_criteria)**  

Get or set the list of filter criteria to apply to the related object.

- 
**[objectName](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_objectName)**  

Get or set the name of the related object to filter by, such as "Account" or "Opportunity".

### criteria

Get or set the list of filter criteria to apply to the related object.

#### Signature

`public List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteria {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.FilterCriteriaInputRepresentation>

### objectName

Get or set the name of the related object to filter by, such as "Account" or "Opportunity".

#### Signature

`public String objectName {get; set;}`

#### Property Value

Type: String
