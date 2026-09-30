---
page_id: apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm
title: SearchProductsRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-09-29
---

# SearchProductsRepresentation Class

Represents the results of a product search operation, including the list of products, search facets, pagination information, and total count of matching products.

## Namespace

[runtime_industries_cpq](./apex_namespace_runtime_industries_cpq.htm.md)

- 
**[SearchProductsRepresentation Properties](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_properties)**  

Learn more about the properties available with the SearchProductsRepresentation     class.

  

## SearchProductsRepresentation Properties

  
  
  
Learn more about the properties available with the SearchProductsRepresentation
    class.

    
      

The `SearchProductsRepresentation` class includes these
        properties.

    

    
  

- 
**[additionalFields](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_additionalFields)**  

Get or set additional custom fields for the product in the search results.

- 
**[attributeCategories](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_attributeCategories)**  

Get or set the list of attribute categories that contain product attributes for configuration.

- 
**[availabilityDate](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_availabilityDate)**  

Get or set the date when the product becomes available for sale.

- 
**[catalogs](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_catalogs)**  

Get or set the list of catalogs that this product belongs to.

- 
**[childVariationIds](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_childVariationIds)**  

Get the list of IDs of the child variations of the product.

- 
**[configureDuringSale](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_configureDuringSale)**  

Get or set whether the product can be configured during the sales process.

- 
**[description](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_description)**  

Get or set the description of the product in the search results. If data translation is set up and specified in the org, the translated description is available.

- 
**[discontinuedDate](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_discontinuedDate)**  

Get or set the date when the product was discontinued.

- 
**[displayUrl](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_displayUrl)**  

Get or set the URL to display additional information about the product.

- 
**[endOfLifeDate](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_endOfLifeDate)**  

Get or set the end of life date for the product.

- 
**[id](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_id)**  

Get or set the ID of the product in the search results.

- 
**[isActive](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_isActive)**  

Get or set whether the product is active (true) or not (false) in the search results.

- 
**[isAssetizable](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_isAssetizable)**  

Get or set whether the product can be converted to an asset after sale.

- 
**[isComponentRequired](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_isComponentRequired)**  

Get or set whether this component is required in a bundle or product relationship.

- 
**[isDefaultComponent](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_isDefaultComponent)**  

Get or set whether this component is selected by default in a bundle or product relationship.

- 
**[isQuantityEditable](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_isQuantityEditable)**  

Get or set whether the quantity of this product can be edited.

- 
**[isSoldOnlyWithOtherProds](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_isSoldOnlyWithOtherProds)**  

Get or set whether this product can only be sold with other products.

- 
**[name](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_name)**  

Get or set the name of the product in the search results. If data translation is set up and specified in the org, the translated name is available.

- 
**[nodeType](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_nodeType)**  

Get or set the node type of the product, such as "Product" or "Bundle".

- 
**[prices](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_prices)**  

Get or set the list of prices available for this product.

- 
**[productCategories](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productCategories)**  

Get the list of categories that the product belongs to.

- 
**[productClass](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productClass)**  

Get the class of the product.

- 
**[productClassification](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productClassification)**  

Get or set the product classification information for this product.

- 
**[productCode](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productCode)**  

Get or set the universal product code that's used to track the part that's used in the product.

- 
**[productComponentGroups](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productComponentGroups)**  

Get or set the list of product component groups that organize related components.

- 
**[productInformation](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productInformation)**  

Get or set additional product information details.

- 
**[productPricingInformation](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productPricingInformation)**  

Get or set the pricing information for this product, including price lists and pricing models.

- 
**[productQuantity](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productQuantity)**  

Get or set the quantity constraints and current quantity for this product.

- 
**[productRelatedComponent](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productRelatedComponent)**  

Get or set the related component information for this product in bundle or product relationships.

- 
**[productSellingModelOptions](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productSellingModelOptions)**  

Get or set the list of selling model options available for this product.

- 
**[productSpecificationType](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_productSpecificationType)**  

Get or set the product specification type that defines the structure and attributes for configuring this product.

- 
**[productType](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productType)**  

Get or set the type of product, such as "Product", "Service", or "Bundle".

- 
**[productUnitOfMeasures](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_productUnitOfMeasures)**  

Get the list of units of measure for the product.

- 
**[qualificationContext](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_ricpq_SearchProductsR_qualificationContext)**  

Get or set the qualification context that contains the qualification result and reason for this product.

- 
**[status](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_status)**  

Get or set the status of the product, such as "Active" or "Inactive".

- 
**[unitOfMeasure](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_unitOfMeasure)**  

Get or set the unit of measure for the quantity of this product.

- 
**[variationAttributeSet](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_variationAttributeSet)**  

Get the variation attribute set of the product.

- 
**[variationsCount](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsRepresentation_variationsCount)**  

Get the number of variations of the product.

### additionalFields

Get or set additional custom fields for the product in the search results.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AdditionalFieldsWrapper>

### attributeCategories

Get or set the list of attribute categories that contain product attributes for configuration.

#### Signature

`public List<runtime_industries_cpq.AttributeCategoryOutputRepresentation> attributeCategories {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.AttributeCategoryOutputRepresentation>

### availabilityDate

Get or set the date when the product becomes available for sale.

#### Signature

`public Datetime availabilityDate {get; set;}`

#### Property Value

Type: Datetime

### catalogs

Get or set the list of catalogs that this product belongs to.

#### Signature

`public List<runtime_industries_cpq.CatalogOutputRepresentation> catalogs {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.CatalogOutputRepresentation>

### childVariationIds

Get the list of IDs of the child variations of the product.

#### Signature

`public List<String> childVariationIds {get; set;}`

#### Property Value

Type: List<String>

### configureDuringSale

Get or set whether the product can be configured during the sales process.

#### Signature

`public String configureDuringSale {get; set;}`

#### Property Value

Type: String

### description

Get or set the description of the product in the search results. If data translation is set up and specified in the org, the translated description is available.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### discontinuedDate

Get or set the date when the product was discontinued.

#### Signature

`public Datetime discontinuedDate {get; set;}`

#### Property Value

Type: Datetime

### displayUrl

Get or set the URL to display additional information about the product.

#### Signature

`public String displayUrl {get; set;}`

#### Property Value

Type: String

### endOfLifeDate

Get or set the end of life date for the product.

#### Signature

`public Datetime endOfLifeDate {get; set;}`

#### Property Value

Type: Datetime

### id

Get or set the ID of the product in the search results.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isActive

Get or set whether the product is active (true) or not (false) in the search results.

#### Signature

`public Boolean isActive {get; set;}`

#### Property Value

Type: Boolean

### isAssetizable

Get or set whether the product can be converted to an asset after sale.

#### Signature

`public Boolean isAssetizable {get; set;}`

#### Property Value

Type: Boolean

### isComponentRequired

Get or set whether this component is required in a bundle or product relationship.

#### Signature

`public Boolean isComponentRequired {get; set;}`

#### Property Value

Type: Boolean

### isDefaultComponent

Get or set whether this component is selected by default in a bundle or product relationship.

#### Signature

`public Boolean isDefaultComponent {get; set;}`

#### Property Value

Type: Boolean

### isQuantityEditable

Get or set whether the quantity of this product can be edited.

#### Signature

`public Boolean isQuantityEditable {get; set;}`

#### Property Value

Type: Boolean

### isSoldOnlyWithOtherProds

Get or set whether this product can only be sold with other products.

#### Signature

`public Boolean isSoldOnlyWithOtherProds {get; set;}`

#### Property Value

Type: Boolean

### name

Get or set the name of the product in the search results. If data translation is set up and specified in the org, the translated name is available.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### nodeType

Get or set the node type of the product, such as "Product" or "Bundle".

#### Signature

`public String nodeType {get; set;}`

#### Property Value

Type: String

### prices

Get or set the list of prices available for this product.

#### Signature

`public List<runtime_industries_cpq.ProductPricesOutputRepresentation> prices {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.ProductPricesOutputRepresentation>

### productCategories

Get the list of categories that the product belongs to.

#### Signature

`public List<runtime_industries_cpq.CategoryOutputRepresentation> productCategories {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.CategoryOutputRepresentation](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_CategoryOutputRepresentation)>

### productClass

Get the class of the product.

#### Signature

`public String productClass {get; set;}`

#### Property Value

Type: String

### productClassification

Get or set the product classification information for this product.

#### Signature

`public runtime_industries_cpq.ProductClassificationOutputRepresentation productClassification {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductClassificationOutputRepresentation

### productCode

Get or set the universal product code that's used to track the part that's used in the product.

#### Signature

`public String productCode {get; set;}`

#### Property Value

Type: String

### productComponentGroups

Get or set the list of product component groups that organize related components.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation> productComponentGroups {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation>

### productInformation

Get or set additional product information details.

#### Signature

`public String productInformation {get; set;}`

#### Property Value

Type: String

### productPricingInformation

Get or set the pricing information for this product, including price lists and pricing models.

#### Signature

`public String productPricingInformation {get; set;}`

#### Property Value

Type: String

### productQuantity

Get or set the quantity constraints and current quantity for this product.

#### Signature

`public runtime_industries_cpq.ProductQuantityOutputRepresentation productQuantity {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductQuantityOutputRepresentation

### productRelatedComponent

Get or set the related component information for this product in bundle or product relationships.

#### Signature

`public ConnectApi.CPQProductRelatedComponentOutputRepresentation productRelatedComponent {get; set;}`

#### Property Value

Type: ConnectApi.CPQProductRelatedComponentOutputRepresentation

### productSellingModelOptions

Get or set the list of selling model options available for this product.

#### Signature

`public List<runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation> productSellingModelOptions {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.ProductSellingModelOptionOutputRepresentation>

### productSpecificationType

Get or set the product specification type that defines the structure and attributes for configuring this product.

#### Signature

`public runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation productSpecificationType {get; set;}`

#### Property Value

Type: runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation

### productType

Get or set the type of product, such as "Product", "Service", or "Bundle".

#### Signature

`public String productType {get; set;}`

#### Property Value

Type: String

### productUnitOfMeasures

Get the list of units of measure for the product.

#### Signature

`public List<runtime_industries_cpq.ProductUnitOfMeasureOutputRepresentation> productUnitOfMeasures {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.ProductUnitOfMeasureOutputRepresentation](./apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductUnitOfMeasureOutputRepresentation)>

### qualificationContext

Get or set the qualification context that contains the qualification result and reason for this product.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: runtime_industries_cpq.QualificationContextOutputRepresentation

### status

Get or set the status of the product, such as "Active" or "Inactive".

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String

### unitOfMeasure

Get or set the unit of measure for the quantity of this product.

#### Signature

`public ConnectApi.UnitOfMeasureOutputRepresentation unitOfMeasure {get; set;}`

#### Property Value

Type: ConnectApi.UnitOfMeasureOutputRepresentation

### variationAttributeSet

Get the variation attribute set of the product.

#### Signature

`public runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation variationAttributeSet {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.ProductVariantAttributeSetOutputRepresentation](./apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductVariantAttributeSetOutputRepresentation)

### variationsCount

Get the number of variations of the product.

#### Signature

`public Integer variationsCount {get; set;}`

#### Property Value

Type: Integer
