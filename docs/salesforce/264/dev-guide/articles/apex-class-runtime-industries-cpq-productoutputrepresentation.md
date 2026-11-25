---
page_id: apex-class-runtime-industries-cpq-productoutputrepresentation
title: ProductOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm
fetched_at: 2026-11-25
---

# ProductOutputRepresentation Class

Get the details of a product definition.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[ProductOutputRepresentation Properties](#productoutputrepresentation-properties)**

Learn more about the properties available with the ProductOutputRepresentation class.

## ProductOutputRepresentation Properties

Learn more about the properties available with the ProductOutputRepresentation class.

The `ProductOutputRepresentation` class includes these properties.

- 

**[additionalFields](#additionalfields)**

Get the key-value pair of additional standard or custom fields with their values.

- 

**[attributeCategories](#attributecategories)**

Get the list of categorized attributes related to the product.

- 

**[availabilityDate](#availabilitydate)**

Get the date when the part is used in the product or is made available for sale.

- 

**[catalogs](#catalogs)**

Get the list of associated catalogs. Returns the name and id values only.

- 

**[childVariationIds](#childvariationids)**

Get the list of IDs of the child variations of the product.

- 

**[configureDuringSale](#configureduringsale)**

Determines whether to allow or prevent configuration when a bundle is sold.

- 

**[description](#description)**

Get the description of the product. If data translation is set up and specified in the org, the translated description is available.

- 

**[discontinuedDate](#discontinueddate)**

Get the date from when the part can’t be used in the product or sold.

- 

**[displayUrl](#displayurl)**

Get the display image URL of the product.

- 

**[endOfLifeDate](#endoflifedate)**

Get the date after which a product isn’t supported, ordered, or maintained.

- 

**[id](#id)**

Get the ID of the product.

- 

**[isActive](#isactive)**

Indicates whether the product is active (true) or not (false).

- 

**[isAssetizable](#isassetizable)**

Indicates whether the product instance remains a customer asset after it’s purchased (true) or not (false).

- 

**[isComponentRequired](#iscomponentrequired)**

Indicates whether the product component is required (true) or not (false).

- 

**[isDefaultComponent](#isdefaultcomponent)**

Indicates whether the product component is the default component (true) or not (false).

- 

**[isQuantityEditable](#isquantityeditable)**

Indicates whether the product quantity is editable (true) or not (false).

- 

**[isSoldOnlyWithOtherProds](#issoldonlywithotherprods)**

Indicates whether the product can’t be sold separately (true) or not (false).

- 

**[name](#name)**

Get the name of the product. If data translation is set up and specified in the org, the translated name is available.

- 

**[nodeType](#nodetype)**

Get the type of the node, such as a product or bundled product.

- 

**[productClass](#productclass)**

Get the class of the product.

- 

**[productClassification](#productclassification)**

Get the details of the product classification that the product is based on.

- 

**[productCode](#productcode)**

Get the universal product code that’s used to track the part that’s used in the product.

- 

**[productComponentGroups](#productcomponentgroups)**

Get the logical grouping of the component products in a bundle and group cardinality for ordering the product components.

- 

**[productInformation](#productinformation)**

Get the details of a product.

- 

**[productPricingInformation](#productpricinginformation)**

Get the pricing details of a product.

- 

**[productQuantity](#productquantity)**

Get the quantity of a product.

- 

**[productRelatedComponent](#productrelatedcomponent)**

Get the details of the related components of a product.

- 

**[productSellingModelOptions](#productsellingmodeloptions)**

Get the details of the product selling model options.

- 

**[productSpecificationType](#productspecificationtype)**

Get the details of the product specification type.

- 

**[productType](#producttype)**

Get the product type.

- 

**[qualificationContext](#qualificationcontext)**

Get the context details of a user, which are used for qualification rules.

- 

**[status](#status)**

Get or set the status of the product, such as Active or Inactive.

- 

**[variationAttributeSet](#variationattributeset)**

Get the variation attribute set of the product.

### additionalFields

Get the key-value pair of additional standard or custom fields with their values.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### attributeCategories

Get the list of categorized attributes related to the product.

#### Signature

`public List<runtime_industries_cpq.AttributeCategoryOutputRepresentation> attributeCategories {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.AttributeCategoryOutputRepresentation](./apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation.md#attributecategoryoutputrepresentation-class)>

### availabilityDate

Get the date when the part is used in the product or is made available for sale.

#### Signature

`public Datetime availabilityDate {get; set;}`

#### Property Value

Type: Datetime

### catalogs

Get the list of associated catalogs. Returns the name and id values only.

#### Signature

`public List<runtime_industries_cpq.CatalogOutputRepresentation> catalogs {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.CatalogOutputRepresentation](./apex-class-runtime-industries-cpq-catalogoutputrepresentation.md#catalogoutputrepresentation-class)>

### childVariationIds

Get the list of IDs of the child variations of the product.

#### Signature

`public List<String> childVariationIds {get; set;}`

#### Property Value

Type: List<String>

### configureDuringSale

Determines whether to allow or prevent configuration when a bundle is sold.

#### Signature

`public String configureDuringSale {get; set;}`

#### Property Value

Type: String

### description

Get the description of the product. If data translation is set up and specified in the org, the translated description is available.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### discontinuedDate

Get the date from when the part can’t be used in the product or sold.

#### Signature

`public Datetime discontinuedDate {get; set;}`

#### Property Value

Type: Datetime

### displayUrl

Get the display image URL of the product.

#### Signature

`public String displayUrl {get; set;}`

#### Property Value

Type: String

### endOfLifeDate

Get the date after which a product isn’t supported, ordered, or maintained.

#### Signature

`public Datetime endOfLifeDate {get; set;}`

#### Property Value

Type: Datetime

### id

Get the ID of the product.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isActive

Indicates whether the product is active (true) or not (false).

#### Signature

`public Boolean isActive {get; set;}`

#### Property Value

Type: Boolean

### isAssetizable

Indicates whether the product instance remains a customer asset after it’s purchased (true) or not (false).

#### Signature

`public Boolean isAssetizable {get; set;}`

#### Property Value

Type: Boolean

### isComponentRequired

Indicates whether the product component is required (true) or not (false).

#### Signature

`public Boolean isComponentRequired {get; set;}`

#### Property Value

Type: Boolean

### isDefaultComponent

Indicates whether the product component is the default component (true) or not (false).

#### Signature

`public Boolean isDefaultComponent {get; set;}`

#### Property Value

Type: Boolean

### isQuantityEditable

Indicates whether the product quantity is editable (true) or not (false).

#### Signature

`public Boolean isQuantityEditable {get; set;}`

#### Property Value

Type: Boolean

### isSoldOnlyWithOtherProds

Indicates whether the product can’t be sold separately (true) or not (false).

#### Signature

`public Boolean isSoldOnlyWithOtherProds {get; set;}`

#### Property Value

Type: Boolean

### name

Get the name of the product. If data translation is set up and specified in the org, the translated name is available.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### nodeType

Get the type of the node, such as a product or bundled product.

#### Signature

`public String nodeType {get; set;}`

#### Property Value

Type: String

### productClass

Get the class of the product.

#### Signature

`public String productClass {get; set;}`

#### Property Value

Type: String

### productClassification

Get the details of the product classification that the product is based on.

#### Signature

`public runtime_industries_cpq.ProductClassificationOutputRepresentation productClassification {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductClassificationOutputRepresentation](./apex-class-runtime-industries-cpq-productclassificationoutputrepresentation.md#productclassificationoutputrepresentation-class)

### productCode

Get the universal product code that’s used to track the part that’s used in the product.

#### Signature

`public String productCode {get; set;}`

#### Property Value

Type: String

### productComponentGroups

Get the logical grouping of the component products in a bundle and group cardinality for ordering the product components.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation> productComponentGroups {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductComponentGroupOutputRepresentation](./apex-class-runtime-industries-cpq-productcomponentgroupoutputrepresentation.md#productcomponentgroupoutputrepresentation-class)>

### productInformation

Get the details of a product.

#### Signature

`public String productInformation {get; set;}`

#### Property Value

Type: String

### productPricingInformation

Get the pricing details of a product.

#### Signature

`public String productPricingInformation {get; set;}`

#### Property Value

Type: String

### productQuantity

Get the quantity of a product.

#### Signature

`public runtime_industries_cpq.ProductQuantityOutputRepresentation productQuantity {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductQuantityOutputRepresentation](./apex-class-runtime-industries-cpq-productquantityoutputrepresentation.md#productquantityoutputrepresentation-class)

### productRelatedComponent

Get the details of the related components of a product.

#### Signature

`public ConnectApi.CPQProductRelatedComponentOutputRepresentation productRelatedComponent {get; set;}`

#### Property Value

Type: ConnectApi.CPQProductRelatedComponentOutputRepresentation

### productSellingModelOptions

Get the details of the product selling model options.

#### Signature

`public List<runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation> productSellingModelOptions {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation](./apex-class-ricpq-productsellingmodeloptionor.md#productsellingmodeloptionoutputrepresentation-class)>

### productSpecificationType

Get the details of the product specification type.

#### Signature

`public runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation productSpecificationType {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation](./apex-class-ricpq-productspecificationtypeor.md#productspecificationtypeoutputrepresentation-class)

### productType

Get the product type.

#### Signature

`public String productType {get; set;}`

#### Property Value

Type: String

### qualificationContext

Get the context details of a user, which are used for qualification rules.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.QualificationContextOutputRepresentation](./apex-class-runtime-industries-cpq-qualificationcontextoutputrepresentation.md#qualificationcontextoutputrepresentation-class)

### status

Get or set the status of the product, such as Active or Inactive.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### variationAttributeSet

Get the variation attribute set of the product.

#### Signature

`public runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation variationAttributeSet {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation](./apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat.md#productvariantattributesetoutputrepresentation-class)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-productoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
