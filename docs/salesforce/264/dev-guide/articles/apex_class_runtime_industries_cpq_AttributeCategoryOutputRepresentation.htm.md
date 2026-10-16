---
page_id: apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm
title: AttributeCategoryOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-09-29
---

# AttributeCategoryOutputRepresentation Class

Stores details of an attribute such as code, description, usage type, and so
    on.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[AttributeCategoryOutputRepresentation Properties](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_properties)**  

Contains properties to include details of an attribute.

  

## AttributeCategoryOutputRepresentation Properties

  
  
  
Contains properties to include details of an attribute.

    
      

The `AttributeCategoryOutputRepresentation` class includes
        these properties.

    

    
  

- 
**[code](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_code)**  

Get the code of the attribute category.

- 
**[description](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_ricpq_AttributeCategoryOR_description)**  

Get the description of the attribute category.

- 
**[id](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_id)**  

Get the ID of the attribute category.

- 
**[name](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_name)**  

Get the name of the attribute category.

- 
**[records](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_records)**  

Get the attributes of the attribute category.

- 
**[sequence](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_sequence)**  

Get the sequence of the attribute category.

- 
**[status](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_status)**  

Get the status of the attribute category.

- 
**[totalSize](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_totalSize)**  

Get the total size of the attribute category.

- 
**[usageType](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_AttributeCategoryOutputRepresentation_usageType)**  

Get the usage type of the attribute category.

### code

Get the code of the attribute category.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### description

Get the description of the attribute category.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the attribute category.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the attribute category.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### records

Get the attributes of the attribute category.

#### Signature

`public List<runtime_industries_cpq.ProductAttributeOutputRepresentation> records {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductAttributeOutputRepresentation](./apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation)>

### sequence

Get the sequence of the attribute category.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

### status

Get the status of the attribute category.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### totalSize

Get the total size of the attribute category.

#### Signature

`public Integer totalSize {get; set;}`

#### Property Value

Type: Integer

### usageType

Get the usage type of the attribute category.

#### Signature

`public String usageType {get; set;}`

#### Property Value

Type: String
