---
page_id: apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm
title: BulkProductDetailsRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-11-23
---

# BulkProductDetailsRepresentation Class

Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[BulkProductDetailsRepresentation Constructor](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_constructors)**  
  Learn more about the constructors that are available with the BulkProductDetailsRepresentation class.
- **[BulkProductDetailsRepresentation Properties](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_properties)**  
  Contains properties to include details of product definitions retrieved in bulk operations.

## BulkProductDetailsRepresentation Constructor

Learn more about the constructors that are available with the BulkProductDetailsRepresentation
class.

The `BulkProductDetailsRepresentation` class includes these
constructors.

- **[BulkProductDetailsRepresentation(apexObj)](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_ctor)**  
  Constructor to create a BulkProductDetailsRepresentation instance from a ConnectApi CPQProductDetailsOutputRepresentation object.
- **[BulkProductDetailsRepresentation()](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_ctor_2)**  
  Default constructor to create an empty BulkProductDetailsRepresentation instance.

### BulkProductDetailsRepresentation(apexObj)

Constructor to create a BulkProductDetailsRepresentation instance from a ConnectApi CPQProductDetailsOutputRepresentation object.

#### Signature

`public BulkProductDetailsRepresentation(ConnectApi.CPQProductDetailsOutputRepresentation apexObj)`

#### Parameters

**apexObj**

Type: ConnectApi.CPQProductDetailsOutputRepresentation

The ConnectApi product details representation object to convert to BulkProductDetailsRepresentation.

### BulkProductDetailsRepresentation()

Default constructor to create an empty BulkProductDetailsRepresentation instance.

#### Signature

`public BulkProductDetailsRepresentation()`

## BulkProductDetailsRepresentation Properties

Contains properties to include details of product definitions retrieved in bulk operations.

The `BulkProductDetailsRepresentation` class includes these
properties.

- **[additionalFields](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_additionalFields)**  
  Get the list of additionalfield.
- **[attributeCategories](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_attributeCategories)**  
  Get the list of attributecategorie.
- **[attributes](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_attributes)**  
  Get the list of attribute.
- **[availabilityDate](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_availabilityDate)**  
  Get the availability date.
- **[catalogs](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_catalogs)**  
  Get the list of catalog.
- **[childProducts](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_childProducts)**  
  Get the list of childproduct.
- **[childVariationIds](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_childVariationIds)**  
  Get the list of IDs of the child variations of the product.
- **[configureDuringSale](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_configureDuringSale)**  
  Get the configureduringsale value.
- **[description](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_description)**  
  Get the description of the bulkproductdetails.
- **[discontinuedDate](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_discontinuedDate)**  
  Get the discontinued date.
- **[displayUrl](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_displayUrl)**  
  Get the displayurl value.
- **[endOfLifeDate](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_endOfLifeDate)**  
  Get the endoflife date.
- **[isActive](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_isActive)**  
  Indicates whether the item is active.
- **[isAssetizable](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_isAssetizable)**  
  Indicates whether assetizable is true or false.
- **[isComponentRequired](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_isComponentRequired)**  
  Indicates whether componentrequired is true or false.
- **[id](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_id)**  
  Get the ID of the product.
- **[isDefaultComponent](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_isDefaultComponent)**  
  Indicates whether defaultcomponent is true or false.
- **[isQuantityEditable](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_isQuantityEditable)**  
  Indicates whether quantityeditable is true or false.
- **[isSoldOnlyWithOtherProds](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_isSoldOnlyWithOtherProds)**  
  Indicates whether soldonlywithotherprods is true or false.
- **[name](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_name)**  
  Get the name of the bulkproductdetails.
- **[nodeType](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_nodeType)**  
  Get the nodetype value.
- **[prices](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_prices)**  
  Get the list of price.
- **[productClass](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_productClass)**  
  Get the class of the product.
- **[productClassification](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productClassification)**  
  Get the productclassification value.
- **[productCode](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_productCode)**  
  Get the productcode value.
- **[productComponentGroups](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productComponentGroups)**  
  Get the list of productcomponentgroup.
- **[productInformation](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productInformation)**  
  Get the productinformation value.
- **[productPricingInformation](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productPricingInformation)**  
  Get the productpricinginformation value.
- **[productQuantity](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_productQuantity)**  
  Get the productquantity value.
- **[productRelatedComponent](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productRelatedComponent)**  
  Get the productrelatedcomponent value.
- **[productSellingModelOptions](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productSellingModelOptions)**  
  Get the list of productsellingmodeloption.
- **[productSpecificationType](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_productSpecificationType)**  
  Get the productspecificationtype value.
- **[productType](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_productType)**  
  Get the producttype value.
- **[productUnitOfMeasures](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_productUnitOfMeasures)**  
  Get the list of units of measure for the product.
- **[qualificationContext](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_ricpq_BulkProductDetailsR_qualificationContext)**  
  Get the qualificationcontext value.
- **[status](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_status)**  
  Get the status of the bulkproductdetails.
- **[unitOfMeasure](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_unitOfMeasure)**  
  Get the unitofmeasure value.
- **[variationAttributeSet](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md#apex_runtime_industries_cpq_BulkProductDetailsRepresentation_variationAttributeSet)**  
  Get the variation attribute set of the product.

### additionalFields

Get the list of additionalfield.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime\_industries\_cpq.AdditionalFieldsWrapper>

### attributeCategories

Get the list of attributecategorie.

#### Signature

`public List<runtime_industries_cpq.AttributeCategoryOutputRepresentation> attributeCategories {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.AttributeCategoryOutputRepresentation](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation "Stores details of an attribute such as code, description, usage type, and so on.")>

### attributes

Get the list of attribute.

#### Signature

`public List<runtime_industries_cpq.ProductAttributeOutputRepresentation> attributes {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductAttributeOutputRepresentation](./apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation "Contains details about the attribute in a product configuration.")>

### availabilityDate

Get the availability date.

#### Signature

`public Datetime availabilityDate {get; set;}`

#### Property Value

Type: Datetime

### catalogs

Get the list of catalog.

#### Signature

`public List<runtime_industries_cpq.CatalogOutputRepresentation> catalogs {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.CatalogOutputRepresentation](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_CatalogOutputRepresentation "Contains properties to store details of a catalog definition.")>

### childProducts

Get the list of childproduct.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsRepresentation> childProducts {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.BulkProductDetailsRepresentation](#apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation "Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.")>

### childVariationIds

Get the list of IDs of the child variations of the product.

#### Signature

`public List<String> childVariationIds {get; set;}`

#### Property Value

Type: List<String>

### configureDuringSale

Get the configureduringsale value.

#### Signature

`public String configureDuringSale {get; set;}`

#### Property Value

Type: String

### description

Get the description of the bulkproductdetails.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### discontinuedDate

Get the discontinued date.

#### Signature

`public Datetime discontinuedDate {get; set;}`

#### Property Value

Type: Datetime

### displayUrl

Get the displayurl value.

#### Signature

`public String displayUrl {get; set;}`

#### Property Value

Type: String

### endOfLifeDate

Get the endoflife date.

#### Signature

`public Datetime endOfLifeDate {get; set;}`

#### Property Value

Type: Datetime

### isActive

Indicates whether the item is active.

#### Signature

`public Boolean isActive {get; set;}`

#### Property Value

Type: Boolean

### isAssetizable

Indicates whether assetizable is true or false.

#### Signature

`public Boolean isAssetizable {get; set;}`

#### Property Value

Type: Boolean

### isComponentRequired

Indicates whether componentrequired is true or false.

#### Signature

`public Boolean isComponentRequired {get; set;}`

#### Property Value

Type: Boolean

### id

Get the ID of the product.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isDefaultComponent

Indicates whether defaultcomponent is true or false.

#### Signature

`public Boolean isDefaultComponent {get; set;}`

#### Property Value

Type: Boolean

### isQuantityEditable

Indicates whether quantityeditable is true or false.

#### Signature

`public Boolean isQuantityEditable {get; set;}`

#### Property Value

Type: Boolean

### isSoldOnlyWithOtherProds

Indicates whether soldonlywithotherprods is true or false.

#### Signature

`public Boolean isSoldOnlyWithOtherProds {get; set;}`

#### Property Value

Type: Boolean

### name

Get the name of the bulkproductdetails.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### nodeType

Get the nodetype value.

#### Signature

`public String nodeType {get; set;}`

#### Property Value

Type: String

### prices

Get the list of price.

#### Signature

`public List<runtime_industries_cpq.ProductPricesOutputRepresentation> prices {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductPricesOutputRepresentation](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation "Get the price details of a product.")>

### productClass

Get the class of the product.

#### Signature

`public String productClass {get; set;}`

#### Property Value

Type: String

### productClassification

Get the productclassification value.

#### Signature

`public runtime_industries_cpq.ProductClassificationOutputRepresentation productClassification {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductClassificationOutputRepresentation](./apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation "Get details of the product classification in a product configuration.")

### productCode

Get the productcode value.

#### Signature

`public String productCode {get; set;}`

#### Property Value

Type: String

### productComponentGroups

Get the list of productcomponentgroup.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupRepresentation> productComponentGroups {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductComponentGroupRepresentation](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation "Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.")>

### productInformation

Get the productinformation value.

#### Signature

`public String productInformation {get; set;}`

#### Property Value

Type: String

### productPricingInformation

Get the productpricinginformation value.

#### Signature

`public String productPricingInformation {get; set;}`

#### Property Value

Type: String

### productQuantity

Get the productquantity value.

#### Signature

`public runtime_industries_cpq.ProductQuantityOutputRepresentation productQuantity {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductQuantityOutputRepresentation](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation "Represents the quantity constraints and current quantity for a product in the product discovery context.")

### productRelatedComponent

Get the productrelatedcomponent value.

#### Signature

`public runtime_industries_cpq.ProductRelatedComponentOutputRepresentation productRelatedComponent {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductRelatedComponentOutputRepresentation](./apex_class_ricpq_ProductRelatedComponentOR.htm.md#apex_class_ricpq_ProductRelatedComponentOR "Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.")

### productSellingModelOptions

Get the list of productsellingmodeloption.

#### Signature

`public List<runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation> productSellingModelOptions {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductSellingModelOptionOutputRepresentation](./apex_class_ricpq_ProductSellingModelOptionOR.htm.md#apex_class_ricpq_ProductSellingModelOptionOR "Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).")>

### productSpecificationType

Get the productspecificationtype value.

#### Signature

`public runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation productSpecificationType {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductSpecificationTypeOutputRepresentation](./apex_class_ricpq_ProductSpecificationTypeOR.htm.md#apex_class_ricpq_ProductSpecificationTypeOR "Represents a product specification type that defines the structure and attributes available for configuring a product.")

### productType

Get the producttype value.

#### Signature

`public String productType {get; set;}`

#### Property Value

Type: String

### productUnitOfMeasures

Get the list of units of measure for the product.

#### Signature

`public List<runtime_industries_cpq.ProductUnitOfMeasureOutputRepresentation> productUnitOfMeasures {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductUnitOfMeasureOutputRepresentation](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation "Represents a unit of measure that's available for a product, including whether it's the base or default unit and whether it's orderable.")>

### qualificationContext

Get the qualificationcontext value.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.QualificationContextOutputRepresentation](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation "Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.")

### status

Get the status of the bulkproductdetails.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### unitOfMeasure

Get the unitofmeasure value.

#### Signature

`public runtime_industries_cpq.UnitOfMeasureOutputRepresentation unitOfMeasure {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.UnitOfMeasureOutputRepresentation](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation "Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.")

### variationAttributeSet

Get the variation attribute set of the product.

#### Signature

`public runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation variationAttributeSet {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductVariantAttributeSetOutputRepresentation](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation "Stores the set of attributes that define the variations of a product.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
