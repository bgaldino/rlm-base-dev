---
page_id: apex-class-runtime-industries-cpq-bulkproductdetailsrepresentation
title: BulkProductDetailsRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-bulkproductdetailsrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm
fetched_at: 2026-11-25
---

# BulkProductDetailsRepresentation Class

Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[BulkProductDetailsRepresentation Constructor](#bulkproductdetailsrepresentation-constructor)**

Learn more about the constructors that are available with the BulkProductDetailsRepresentation class.

- 

**[BulkProductDetailsRepresentation Properties](#bulkproductdetailsrepresentation-properties)**

Contains properties to include details of product definitions retrieved in bulk operations.

## BulkProductDetailsRepresentation Constructor

Learn more about the constructors that are available with the BulkProductDetailsRepresentation class.

The `BulkProductDetailsRepresentation` class includes these constructors.

- 

**[BulkProductDetailsRepresentation(apexObj)](#bulkproductdetailsrepresentationapexobj)**

Constructor to create a BulkProductDetailsRepresentation instance from a ConnectApi CPQProductDetailsOutputRepresentation object.

- 

**[BulkProductDetailsRepresentation()](#bulkproductdetailsrepresentation)**

Default constructor to create an empty BulkProductDetailsRepresentation instance.

### BulkProductDetailsRepresentation(apexObj)

Constructor to create a BulkProductDetailsRepresentation instance from a ConnectApi CPQProductDetailsOutputRepresentation object.

#### Signature

`public BulkProductDetailsRepresentation(ConnectApi.CPQProductDetailsOutputRepresentation apexObj)`

#### Parameters

***apexObj***

Type: ConnectApi.CPQProductDetailsOutputRepresentation

The ConnectApi product details representation object to convert to BulkProductDetailsRepresentation.

### BulkProductDetailsRepresentation()

Default constructor to create an empty BulkProductDetailsRepresentation instance.

#### Signature

`public BulkProductDetailsRepresentation()`

## BulkProductDetailsRepresentation Properties

Contains properties to include details of product definitions retrieved in bulk operations.

The `BulkProductDetailsRepresentation` class includes these properties.

- 

**[additionalFields](#additionalfields)**

Get the list of additionalfield.

- 

**[attributeCategories](#attributecategories)**

Get the list of attributecategorie.

- 

**[attributes](#attributes)**

Get the list of attribute.

- 

**[availabilityDate](#availabilitydate)**

Get the availability date.

- 

**[catalogs](#catalogs)**

Get the list of catalog.

- 

**[childProducts](#childproducts)**

Get the list of childproduct.

- 

**[childVariationIds](#childvariationids)**

Get the list of IDs of the child variations of the product.

- 

**[configureDuringSale](#configureduringsale)**

Get the configureduringsale value.

- 

**[description](#description)**

Get the description of the bulkproductdetails.

- 

**[discontinuedDate](#discontinueddate)**

Get the discontinued date.

- 

**[displayUrl](#displayurl)**

Get the displayurl value.

- 

**[endOfLifeDate](#endoflifedate)**

Get the endoflife date.

- 

**[isActive](#isactive)**

Indicates whether the item is active.

- 

**[isAssetizable](#isassetizable)**

Indicates whether assetizable is true or false.

- 

**[isComponentRequired](#iscomponentrequired)**

Indicates whether componentrequired is true or false.

- 

**[id](#id)**

Get the ID of the product.

- 

**[isDefaultComponent](#isdefaultcomponent)**

Indicates whether defaultcomponent is true or false.

- 

**[isQuantityEditable](#isquantityeditable)**

Indicates whether quantityeditable is true or false.

- 

**[isSoldOnlyWithOtherProds](#issoldonlywithotherprods)**

Indicates whether soldonlywithotherprods is true or false.

- 

**[name](#name)**

Get the name of the bulkproductdetails.

- 

**[nodeType](#nodetype)**

Get the nodetype value.

- 

**[prices](#prices)**

Get the list of price.

- 

**[productClass](#productclass)**

Get the class of the product.

- 

**[productClassification](#productclassification)**

Get the productclassification value.

- 

**[productCode](#productcode)**

Get the productcode value.

- 

**[productComponentGroups](#productcomponentgroups)**

Get the list of productcomponentgroup.

- 

**[productInformation](#productinformation)**

Get the productinformation value.

- 

**[productPricingInformation](#productpricinginformation)**

Get the productpricinginformation value.

- 

**[productQuantity](#productquantity)**

Get the productquantity value.

- 

**[productRelatedComponent](#productrelatedcomponent)**

Get the productrelatedcomponent value.

- 

**[productSellingModelOptions](#productsellingmodeloptions)**

Get the list of productsellingmodeloption.

- 

**[productSpecificationType](#productspecificationtype)**

Get the productspecificationtype value.

- 

**[productType](#producttype)**

Get the producttype value.

- 

**[productUnitOfMeasures](#productunitofmeasures)**

Get the list of units of measure for the product.

- 

**[qualificationContext](#qualificationcontext)**

Get the qualificationcontext value.

- 

**[status](#status)**

Get the status of the bulkproductdetails.

- 

**[unitOfMeasure](#unitofmeasure)**

Get the unitofmeasure value.

- 

**[variationAttributeSet](#variationattributeset)**

Get the variation attribute set of the product.

### additionalFields

Get the list of additionalfield.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### attributeCategories

Get the list of attributecategorie.

#### Signature

`public List<runtime_industries_cpq.AttributeCategoryOutputRepresentation> attributeCategories {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.AttributeCategoryOutputRepresentation](./apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation.md#attributecategoryoutputrepresentation-class)>

### attributes

Get the list of attribute.

#### Signature

`public List<runtime_industries_cpq.ProductAttributeOutputRepresentation> attributes {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductAttributeOutputRepresentation](./apex-class-runtime-industries-cpq-productattributeoutputrepresentation.md#productattributeoutputrepresentation-class)>

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

Type: List<[runtime_industries_cpq.CatalogOutputRepresentation](./apex-class-runtime-industries-cpq-catalogoutputrepresentation.md#catalogoutputrepresentation-class)>

### childProducts

Get the list of childproduct.

#### Signature

`public List<runtime_industries_cpq.BulkProductDetailsRepresentation> childProducts {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.BulkProductDetailsRepresentation](#bulkproductdetailsrepresentation-class)>

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

Type: List<[runtime_industries_cpq.ProductPricesOutputRepresentation](./apex-class-runtime-industries-cpq-productpricesoutputrepresentation.md#productpricesoutputrepresentation-class)>

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

Type: [runtime_industries_cpq.ProductClassificationOutputRepresentation](./apex-class-runtime-industries-cpq-productclassificationoutputrepresentation.md#productclassificationoutputrepresentation-class)

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

Type: List<[runtime_industries_cpq.ProductComponentGroupRepresentation](./apex-class-runtime-industries-cpq-productcomponentgrouprepresentation.md#productcomponentgrouprepresentation-class)>

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

Type: [runtime_industries_cpq.ProductQuantityOutputRepresentation](./apex-class-runtime-industries-cpq-productquantityoutputrepresentation.md#productquantityoutputrepresentation-class)

### productRelatedComponent

Get the productrelatedcomponent value.

#### Signature

`public runtime_industries_cpq.ProductRelatedComponentOutputRepresentation productRelatedComponent {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductRelatedComponentOutputRepresentation](./apex-class-ricpq-productrelatedcomponentor.md#productrelatedcomponentoutputrepresentation-class)

### productSellingModelOptions

Get the list of productsellingmodeloption.

#### Signature

`public List<runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation> productSellingModelOptions {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation](./apex-class-ricpq-productsellingmodeloptionor.md#productsellingmodeloptionoutputrepresentation-class)>

### productSpecificationType

Get the productspecificationtype value.

#### Signature

`public runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation productSpecificationType {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation](./apex-class-ricpq-productspecificationtypeor.md#productspecificationtypeoutputrepresentation-class)

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

Type: List<[runtime_industries_cpq.ProductUnitOfMeasureOutputRepresentation](./apex-class-runtime-industries-cpq-productunitofmeasureoutputrepresentation.md#productunitofmeasureoutputrepresentation-class)>

### qualificationContext

Get the qualificationcontext value.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.QualificationContextOutputRepresentation](./apex-class-runtime-industries-cpq-qualificationcontextoutputrepresentation.md#qualificationcontextoutputrepresentation-class)

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

Type: [runtime_industries_cpq.UnitOfMeasureOutputRepresentation](./apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation.md#unitofmeasureoutputrepresentation-class)

### variationAttributeSet

Get the variation attribute set of the product.

#### Signature

`public runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation variationAttributeSet {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation](./apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat.md#productvariantattributesetoutputrepresentation-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-bulkproductdetailsrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
