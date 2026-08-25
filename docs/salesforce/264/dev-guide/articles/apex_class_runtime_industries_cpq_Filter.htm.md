---
page_id: apex_class_runtime_industries_cpq_Filter.htm
title: Filter Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_Filter.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Filter Class

Contains the criteria property to store the details of a filter criteria, which is used
    to filter records.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[Filter Properties](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_runtime_industries_cpq_Filter_properties)**  

Learn more about the properties available with the Filter class.

  

## Filter Properties

  
  
  
Learn more about the properties available with the Filter class.

    
      

The `Filter` class includes these properties.

    

    
  

- 
**[criteria](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_runtime_industries_cpq_Filter_criteria)**  

Get the filter criteria to filter the records.

### criteria

Get the filter criteria to filter the records.

#### Signature

`public List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteria {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.FilterCriteriaInputRepresentation](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation)>
