---
page_id: apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm
title: CatalogOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# CatalogOutputRepresentation Class

Contains properties to store details of a catalog definition.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[CatalogOutputRepresentation Properties](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_properties)**  

Contains properties to include details of a catalog definition.

  

## CatalogOutputRepresentation Properties

  
  
  
Contains properties to include details of a catalog definition.

    
      

The `CatalogOutputRepresentation` class includes these
        properties.

    

    
  

- 
**[catalogCode](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_catalogCode)**  

Get the unique ID associated with the catalog.

- 
**[catalogType](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_catalogType)**  

Get the category of an entry in the catalog, which is customizable. For example, catalog     types, such as sellable products, services, parts, technical services, or technical     resources.

- 
**[customFields](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_customFields)**  

Get details of the custom fields associated with a catalog.

- 
**[description](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_description)**  

Get the description of the catalog.

- 
**[effectiveEndDate](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_effectiveEndDate)**  

Get the date and time from when the catalog isn't available to the end users.

- 
**[effectiveStartDate](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_effectiveStartDate)**  

Get the date and time from when the catalog is available to the end users.

- 
**[id](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_id)**  

Get the ID of the catalog.

- 
**[name](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_name)**  

Get the name of the catalog.

- 
**[numberOfCategories](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_numberOfCategories)**  

Get the number of categories in the catalog.

- 
**[status](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_runtime_industries_cpq_CatalogOutputRepresentation_status)**  

Get the status of the catalog.

### catalogCode

Get the unique ID associated with the catalog.

#### Signature

`public String catalogCode {get; set;}`

#### Property Value

Type: String

### catalogType

Get the category of an entry in the catalog, which is customizable. For example, catalog
    types, such as sellable products, services, parts, technical services, or technical
    resources.

#### Signature

`public String catalogType {get; set;}`

#### Property Value

Type: String

### customFields

Get details of the custom fields associated with a catalog.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> customFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### description

Get the description of the catalog.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### effectiveEndDate

Get the date and time from when the catalog isn't available to the end users.

#### Signature

`public String effectiveEndDate {get; set;}`

#### Property Value

Type: String

### effectiveStartDate

Get the date and time from when the catalog is available to the end users.

#### Signature

`public String effectiveStartDate {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the catalog.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the catalog.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### numberOfCategories

Get the number of categories in the catalog.

#### Signature

`public Integer numberOfCategories {get; set;}`

#### Property Value

Type: Integer

### status

Get the status of the catalog.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String
