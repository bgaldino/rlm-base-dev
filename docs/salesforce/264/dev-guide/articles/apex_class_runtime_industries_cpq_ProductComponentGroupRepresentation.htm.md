---
page_id: apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm
title: ProductComponentGroupRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductComponentGroupRepresentation Class

Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[ProductComponentGroupRepresentation Constructor](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_constructors)**  

Learn more about the constructor that's available with the ProductComponentGroupRepresentation     class.

- 
**[ProductComponentGroupRepresentation Properties](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_properties)**  

Contains properties to include details of a product component group used in bulk operations.

  

## ProductComponentGroupRepresentation Constructor

  
  
  
Learn more about the constructor that's available with the ProductComponentGroupRepresentation
    class.

    
      

The `ProductComponentGroupRepresentation` class includes this
        constructor.

    

    
  

- 
**[ProductComponentGroupRepresentation(apexObj)](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_ctor)**  

Constructor to create a ProductComponentGroupRepresentation instance from a ConnectApi CPQProductComponentGroupOutputRepresentation object.

### ProductComponentGroupRepresentation(apexObj)

Constructor to create a ProductComponentGroupRepresentation instance from a ConnectApi CPQProductComponentGroupOutputRepresentation object.

#### Signature

`public ProductComponentGroupRepresentation(ConnectApi.CPQProductComponentGroupOutputRepresentation apexObj)`

#### Parameters

**apexObj**

: Type: ConnectApi.CPQProductComponentGroupOutputRepresentation

: The ConnectApi product component group representation object to convert to ProductComponentGroupRepresentation.

  

## ProductComponentGroupRepresentation Properties

  
  
  
Contains properties to include details of a product component group used in bulk operations.

    
      

The `ProductComponentGroupRepresentation` class includes these
        properties.

    

    
  

- 
**[childGroups](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_childGroups)**  

Get the list of childgroup.

- 
**[classifications](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_ricpq_ProductComponentGroupR_classifications)**  

Get the list of product classifications.

- 
**[code](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_code)**  

Get the code of the productcomponentgroup.

- 
**[components](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_components)**  

Get the list of component.

- 
**[description](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_description)**  

Get the description of the productcomponentgroup.

- 
**[id](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_id)**  

Get the ID of the productcomponentgroup.

- 
**[name](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_name)**  

Get the name of the productcomponentgroup.

- 
**[parentGroupId](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_ricpq_ProductComponentGroupR_parentGroupId)**  

Get the ID of the parentgroup.

- 
**[parentProductId](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_ricpq_ProductComponentGroupR_parentProductId)**  

Get the ID of the parentproduct.

- 
**[sequence](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupRepresentation_sequence)**  

Get the sequence value.

### childGroups

Get the list of childgroup.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupRepresentation> childGroups {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductComponentGroupRepresentation](#apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation)>

### classifications

Get the list of product classifications.

#### Signature

`public List<runtime_industries_cpq.ProductClassificationOutputRepresentation> classifications {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductClassificationOutputRepresentation](./apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation)>

### code

Get the code of the productcomponentgroup.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### components

Get the list of component.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsRepresentation> components {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.BulkProductDetailsRepresentation](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation)>

### description

Get the description of the productcomponentgroup.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the productcomponentgroup.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the productcomponentgroup.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### parentGroupId

Get the ID of the parentgroup.

#### Signature

`public String parentGroupId {get; set;}`

#### Property Value

Type: String

### parentProductId

Get the ID of the parentproduct.

#### Signature

`public String parentProductId {get; set;}`

#### Property Value

Type: String

### sequence

Get the sequence value.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer
