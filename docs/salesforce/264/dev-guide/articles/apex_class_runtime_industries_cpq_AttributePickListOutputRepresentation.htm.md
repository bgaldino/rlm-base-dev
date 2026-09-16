---
page_id: apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm
title: AttributePickListOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AttributePickListOutputRepresentation Class

Stores details of an attribute picklist.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[AttributePickListOutputRepresentation Properties](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_properties)**  

Contains properties to include details of an attribute picklist.

  

## AttributePickListOutputRepresentation Properties

  
  
  
Contains properties to include details of an attribute picklist.

    
      

The `AttributePickListOutputRepresentation` class includes
        these properties.

    

    
  

- 
**[description](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_ricpq_AttributePickListOR_description)**  

Get the description of the attribute picklist.

- 
**[id](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_id)**  

Get the ID of the attribute picklist.

- 
**[name](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_name)**  

Get the name of the attribute picklist.

- 
**[status](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_status)**  

Get the status of the attribute picklist.

- 
**[values](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_values)**  

Get the values of the attribute picklist.

- 
**[dataType](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributePickListOutputRepresentation_dataType)**  

Get the datatype value.

### description

Get the description of the attribute picklist.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the attribute picklist.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the attribute picklist.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### status

Get the status of the attribute picklist.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### values

Get the values of the attribute picklist.

#### Signature

`public List<runtime_industries_cpq.AttributePickListValueOutputRepresentation> values {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.AttributePickListValueOutputRepresentation](./apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation)>

### dataType

Get the datatype value.

#### Signature

`public String dataType {get; set;}`

#### Property Value

Type: String
