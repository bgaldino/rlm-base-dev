---
page_id: apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm
title: GuidedSelectionSearchTerm Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# GuidedSelectionSearchTerm Class

Represents a search term used in guided product selection. Contains the search term text and associated tags for filtering and searching products in Product Discovery.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[GuidedSelectionSearchTerm Constructor](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_constructors)**  

Learn more about the constructors that are available with the GuidedSelectionSearchTerm     class.

- 
**[GuidedSelectionSearchTerm Properties](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_properties)**  

Contains properties to include search term details for guided product selection.

  

## GuidedSelectionSearchTerm Constructor

  
  
  
Learn more about the constructors that are available with the GuidedSelectionSearchTerm
    class.

    
      

The `GuidedSelectionSearchTerm` class includes these
        constructors.

    

    
  

- 
**[GuidedSelectionSearchTerm(apexObj)](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_ctor)**  

Constructor to create a GuidedSelectionSearchTerm instance from a ConnectApi CPQGuidedSelectionSearchTermOutputRepresentation object.

- 
**[GuidedSelectionSearchTerm()](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_ctor_2)**  

Default constructor to create an empty GuidedSelectionSearchTerm instance.

### GuidedSelectionSearchTerm(apexObj)

Constructor to create a GuidedSelectionSearchTerm instance from a ConnectApi CPQGuidedSelectionSearchTermOutputRepresentation object.

#### Signature

`public GuidedSelectionSearchTerm(ConnectApi.CPQGuidedSelectionSearchTermOutputRepresentation apexObj)`

#### Parameters

**apexObj**

: Type: ConnectApi.CPQGuidedSelectionSearchTermOutputRepresentation

: The ConnectApi guided selection search term representation object to convert to GuidedSelectionSearchTerm.

### GuidedSelectionSearchTerm()

Default constructor to create an empty GuidedSelectionSearchTerm instance.

#### Signature

`public GuidedSelectionSearchTerm()`

  

## GuidedSelectionSearchTerm Properties

  
  
  
Contains properties to include search term details for guided product selection.

    
      

The `GuidedSelectionSearchTerm` class includes these
        properties.

    

    
  

- 
**[tags](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_tags)**  

Get the list of tags.

- 
**[term](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md#apex_runtime_industries_cpq_GuidedSelectionSearchTerm_term)**  

Get the term value.

### tags

Get the list of tags.

#### Signature

`public List<String> tags {get; set;}`

#### Property Value

Type: List<String>

### term

Get the term value.

#### Signature

`public String term {get; set;}`

#### Property Value

Type: String
