---
page_id: apex-class-ricpq-productrelatedcomponentor
title: ProductRelatedComponentOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-ricpq-productrelatedcomponentor.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_ricpq_ProductRelatedComponentOR.htm
fetched_at: 2026-11-25
---

# ProductRelatedComponentOutputRepresentation Class

Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- **[ProductRelatedComponentOutputRepresentation Properties](#productrelatedcomponentoutputrepresentation-properties)**

## ProductRelatedComponentOutputRepresentation Properties

The following are properties for `ProductRelatedComponentOutputRepresentation`.

- 

**[childProductId](#childproductid)**

Get or set the identifier of the child product in the relationship.

- 

**[childSellingModelId](#childsellingmodelid)**

Get or set the identifier of the child product’s selling model in the relationship.

- 

**[doesBundlePriceIncludeChild](#doesbundlepriceincludechild)**

Get or set whether the bundle price includes the price of this child component.

- 

**[id](#id)**

Get or set the unique identifier of the product related component relationship.

- 

**[isComponentRequired](#iscomponentrequired)**

Get or set whether this component is required in the bundle or product relationship.

- 

**[isDefaultComponent](#isdefaultcomponent)**

Get or set whether this component is selected by default in the bundle or product relationship.

- 

**[isQuantityEditable](#isquantityeditable)**

Get or set whether the quantity of this component can be edited.

- 

**[maxQuantity](#maxquantity)**

Get or set the maximum quantity allowed for this component.

- 

**[minQuantity](#minquantity)**

Get or set the minimum quantity required for this component.

- 

**[parentProductId](#parentproductid)**

Get or set the identifier of the parent product in the relationship.

- 

**[parentSellingModelId](#parentsellingmodelid)**

Get or set the identifier of the parent product’s selling model in the relationship.

- 

**[productClassificationId](#productclassificationid)**

Get or set the identifier of the product classification for this component.

- 

**[productComponentGroupId](#productcomponentgroupid)**

Get or set the identifier of the product component group that this component belongs to.

- 

**[productRelationshipTypeId](#productrelationshiptypeid)**

Get or set the identifier of the product relationship type that defines this relationship.

- 

**[quantity](#quantity)**

Get or set the current quantity of this component.

- 

**[quantityScaleMethod](#quantityscalemethod)**

Get or set the method used to scale the quantity of this component, such as “PerUnit” or “PerBundle”.

- 

**[sequence](#sequence)**

Get or set the display sequence order of this component within the bundle or product relationship.

- 

**[unitOfMeasure](#unitofmeasure)**

Get or set the unit of measure for the quantity of this component.

- 

**[isExcluded](#isexcluded)**

Indicates whether excluded is true or false.

- 

**[quoteVisibility](#quotevisibility)**

Get the quotevisibility value.

### childProductId

Get or set the identifier of the child product in the relationship.

#### Signature

`public String childProductId {get; set;}`

#### Property Value

Type: String

### childSellingModelId

Get or set the identifier of the child product’s selling model in the relationship.

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

Get or set the identifier of the parent product’s selling model in the relationship.

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

Get or set the method used to scale the quantity of this component, such as “PerUnit” or “PerBundle”.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-ricpq-productrelatedcomponentor.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
