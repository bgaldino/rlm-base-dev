---
page_id: apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm
title: ProductRelatedComponentOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductRelatedComponentOutputRepresentation Class

Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductRelatedComponentOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_properties)**

## ProductRelatedComponentOutputRepresentation Properties

The following are properties for `ProductRelatedComponentOutputRepresentation`.

- **[childProductId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_childProductId)**  
  Get or set the identifier of the child product in the relationship.
- **[childSellingModelId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_childSellingModelId)**  
  Get or set the identifier of the child product's selling model in the relationship.
- **[doesBundlePriceIncludeChild](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_doesBundlePriceIncludeChild)**  
  Get or set whether the bundle price includes the price of this child component.
- **[id](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_id)**  
  Get or set the unique identifier of the product related component relationship.
- **[isComponentRequired](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_isComponentRequired)**  
  Get or set whether this component is required in the bundle or product relationship.
- **[isDefaultComponent](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_isDefaultComponent)**  
  Get or set whether this component is selected by default in the bundle or product relationship.
- **[isQuantityEditable](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_isQuantityEditable)**  
  Get or set whether the quantity of this component can be edited.
- **[maxQuantity](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_maxQuantity)**  
  Get or set the maximum quantity allowed for this component.
- **[minQuantity](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_minQuantity)**  
  Get or set the minimum quantity required for this component.
- **[parentProductId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_parentProductId)**  
  Get or set the identifier of the parent product in the relationship.
- **[parentSellingModelId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_parentSellingModelId)**  
  Get or set the identifier of the parent product's selling model in the relationship.
- **[productClassificationId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_productClassificationId)**  
  Get or set the identifier of the product classification for this component.
- **[productComponentGroupId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_productComponentGroupId)**  
  Get or set the identifier of the product component group that this component belongs to.
- **[productRelationshipTypeId](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_productRelationshipTypeId)**  
  Get or set the identifier of the product relationship type that defines this relationship.
- **[quantity](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_quantity)**  
  Get or set the current quantity of this component.
- **[quantityScaleMethod](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_quantityScaleMethod)**  
  Get or set the method used to scale the quantity of this component, such as "PerUnit" or "PerBundle".
- **[sequence](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_sequence)**  
  Get or set the display sequence order of this component within the bundle or product relationship.
- **[unitOfMeasure](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_unitOfMeasure)**  
  Get or set the unit of measure for the quantity of this component.
- **[isExcluded](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_isExcluded)**  
  Indicates whether excluded is true or false.
- **[quoteVisibility](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation_quoteVisibility)**  
  Get the quotevisibility value.

### childProductId

Get or set the identifier of the child product in the relationship.

#### Signature

`public String childProductId {get; set;}`

#### Property Value

Type: String

### childSellingModelId

Get or set the identifier of the child product's selling model in the relationship.

#### Signature

`public String childSellingModelId {get; set;}`

#### Property Value

Type: String

### doesBundlePriceIncludeChild

Get or set whether the bundle price includes the price of this child component.

#### Signature

`public Boolean doesBundlePriceIncludeChild {get; set;}`

#### Property Value

Type: Boolean

### id

Get or set the unique identifier of the product related component relationship.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isComponentRequired

Get or set whether this component is required in the bundle or product relationship.

#### Signature

`public Boolean isComponentRequired {get; set;}`

#### Property Value

Type: Boolean

### isDefaultComponent

Get or set whether this component is selected by default in the bundle or product relationship.

#### Signature

`public Boolean isDefaultComponent {get; set;}`

#### Property Value

Type: Boolean

### isQuantityEditable

Get or set whether the quantity of this component can be edited.

#### Signature

`public Boolean isQuantityEditable {get; set;}`

#### Property Value

Type: Boolean

### maxQuantity

Get or set the maximum quantity allowed for this component.

#### Signature

`public Double maxQuantity {get; set;}`

#### Property Value

Type: Double

### minQuantity

Get or set the minimum quantity required for this component.

#### Signature

`public Double minQuantity {get; set;}`

#### Property Value

Type: Double

### parentProductId

Get or set the identifier of the parent product in the relationship.

#### Signature

`public String parentProductId {get; set;}`

#### Property Value

Type: String

### parentSellingModelId

Get or set the identifier of the parent product's selling model in the relationship.

#### Signature

`public String parentSellingModelId {get; set;}`

#### Property Value

Type: String

### productClassificationId

Get or set the identifier of the product classification for this component.

#### Signature

`public String productClassificationId {get; set;}`

#### Property Value

Type: String

### productComponentGroupId

Get or set the identifier of the product component group that this component belongs to.

#### Signature

`public String productComponentGroupId {get; set;}`

#### Property Value

Type: String

### productRelationshipTypeId

Get or set the identifier of the product relationship type that defines this relationship.

#### Signature

`public String productRelationshipTypeId {get; set;}`

#### Property Value

Type: String

### quantity

Get or set the current quantity of this component.

#### Signature

`public Double quantity {get; set;}`

#### Property Value

Type: Double

### quantityScaleMethod

Get or set the method used to scale the quantity of this component, such as "PerUnit" or "PerBundle".

#### Signature

`public String quantityScaleMethod {get; set;}`

#### Property Value

Type: String

### sequence

Get or set the display sequence order of this component within the bundle or product relationship.

#### Signature

`public Integer sequence {get; set;}`

#### Property Value

Type: Integer

### unitOfMeasure

Get or set the unit of measure for the quantity of this component.

#### Signature

`public ConnectApi.UnitOfMeasureOutputRepresentation unitOfMeasure {get; set;}`

#### Property Value

Type: ConnectApi.UnitOfMeasureOutputRepresentation

### isExcluded

Indicates whether excluded is true or false.

#### Signature

`public Boolean isExcluded {get; set;}`

#### Property Value

Type: Boolean

### quoteVisibility

Get the quotevisibility value.

#### Signature

`public String quoteVisibility {get; set;}`

#### Property Value

Type: String
