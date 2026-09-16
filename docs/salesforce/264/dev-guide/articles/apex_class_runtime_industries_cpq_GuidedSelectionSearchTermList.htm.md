---
page_id: apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm
title: GuidedSelectionSearchTermList Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# GuidedSelectionSearchTermList Class

Contains a list of search terms used in guided product selection. This class is used to pass multiple search terms for filtering and searching products in Product Discovery.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[GuidedSelectionSearchTermList Constructor](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTermList_constructors)**  

Learn more about the constructor that's available with the GuidedSelectionSearchTermList     class.

- 
**[GuidedSelectionSearchTermList Properties](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTermList_properties)**  

Contains properties to include a list of search terms for guided product selection.

  

## GuidedSelectionSearchTermList Constructor

  
  
  
Learn more about the constructor that's available with the GuidedSelectionSearchTermList
    class.

    
      

The `GuidedSelectionSearchTermList` class includes this
        constructor.

    

    
  

- 
**[GuidedSelectionSearchTermList()](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTermList_ctor)**  

Default constructor to create an empty GuidedSelectionSearchTermList instance.

### GuidedSelectionSearchTermList()

Default constructor to create an empty GuidedSelectionSearchTermList instance.

#### Signature

`public GuidedSelectionSearchTermList()`

  

## GuidedSelectionSearchTermList Properties

  
  
  
Contains properties to include a list of search terms for guided product selection.

    
      

The `GuidedSelectionSearchTermList` class includes these
        properties.

    

    
  

- 
**[searchTerms](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTermList_searchTerms)**  

Get the list of searchterm.

### searchTerms

Get the list of searchterm.

#### Signature

`public List<runtime_industries_cpq.GuidedSelectionSearchTerm> searchTerms {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.GuidedSelectionSearchTerm](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm)>
