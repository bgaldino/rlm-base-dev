---
page_id: apex_class_runtime_industries_cpq_AdditionalContextData.htm
title: AdditionalContextData Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalContextData.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AdditionalContextData Class

Contains properties to include a list of additional context data nodes. These nodes are
    used along with the context definition nodes for data hydration.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[AdditionalContextData Properties](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md#apex_runtime_industries_cpq_AdditionalContextData_properties)**  

Set the AdditionalContextData class property to specify a list of additional nodes for     data hydration.

  

## AdditionalContextData Properties

  
  
  
Set the AdditionalContextData class property to specify a list of additional nodes for
    data hydration.

    
      

The `AdditionalContextData` class includes this
        property.

    

    
  

- 
**[additionalContextData](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md#apex_runtime_industries_cpq_AdditionalContextData_additionalContextData)**  

Include a list of additional nodes that are used along with the context definition nodes     for data hydration. The maximum number of supported nodes is 10.

### additionalContextData

Include a list of additional nodes that are used along with the context definition nodes
    for data hydration. The maximum number of supported nodes is 10.

#### Signature

`public List<runtime_industries_cpq.ContextDataInput> additionalContextData {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ContextDataInput](./apex_class_runtime_industries_cpq_ContextDataInput.htm.md#apex_class_runtime_industries_cpq_ContextDataInput)>
