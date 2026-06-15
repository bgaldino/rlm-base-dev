---
page_id: apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm
title: ProductComponentGroupOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductComponentGroupOutputRepresentation Class

Get details of the product component group in a product classification.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductComponentGroupOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductComponentGroupOutputRepresentation class.

## ProductComponentGroupOutputRepresentation Properties

Learn more about the properties available with the
ProductComponentGroupOutputRepresentation class.

The `ProductComponentGroupOutputRepresentation` class
includes these properties.

- **[childGroups](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_childGroups)**  
  Get the child groups associated with a product component group.
- **[classifications](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_classifications)**  
  Get the list of classifications for the product component group.
- **[code](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_code)**  
  Get the code of the product component group.
- **[components](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_components)**  
  Get the details of components within the product component group.
- **[description](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_description)**  
  Get the description of the product component group.
- **[id](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_id)**  
  Get the ID of the product component group.
- **[name](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_name)**  
  Get the name of the product component group.
- **[parentGroupId](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_parentGroupId)**  
  Get the ID of the parent group.
- **[parentProductId](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_parentProductId)**  
  Get the parent Product2 ID of the product component group.
- **[sequence](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductComponentGroupOutputRepresentation_sequence)**  
  Get the sequence of the product component group.

### childGroups

Get the child groups associated with a product component group.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation> childGroups {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductComponentGroupOutputRepresentation](#apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation "Get details of the product component group in a product classification.")>

### classifications

Get the list of classifications for the product component group.

#### Signature

`public List<runtime_industries_cpq.ProductClassificationOutputRepresentation> classifications {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductClassificationOutputRepresentation](./apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation "Get details of the product classification in a product configuration.")>

### code

Get the code of the product component group.

#### Signature

`public String code {get; set;}`

#### Property Value

Type: String

### components

Get the details of components within the product component group.

#### Signature

`public List<runtime_industries_cpq.ProductDetailsRepresentation> components {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductDetailsRepresentation](./apex_class_runtime_industries_cpq_ProductDetailsRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductDetailsRepresentation "Get the details of a product definition.")>

### description

Get the description of the product component group.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### id

Get the ID of the product component group.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### name

Get the name of the product component group.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### parentGroupId

Get the ID of the parent group.

#### Signature

`public String parentGroupId {get; set;}`

#### Property Value

Type: String

### parentProductId

Get the parent Product2 ID of the product component group.

#### Signature

`public String parentProductId {get; set;}`

#### Property Value

Type: String

### sequence

Get the sequence of the product component group.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer
