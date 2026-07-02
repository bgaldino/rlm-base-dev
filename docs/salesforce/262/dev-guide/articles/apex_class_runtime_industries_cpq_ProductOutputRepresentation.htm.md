---
page_id: apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm
title: ProductOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# ProductOutputRepresentation Class

Get the details of a product definition.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[ProductOutputRepresentation Properties](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_properties)**  
  Learn more about the properties available with the ProductOutputRepresentation class.

## ProductOutputRepresentation Properties

Learn more about the properties available with the ProductOutputRepresentation
class.

The `ProductOutputRepresentation` class includes these
properties.

- **[additionalFields](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_additionalFields)**  
  Get the key-value pair of additional standard or custom fields with their values.
- **[attributeCategories](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_attributeCategories)**  
  Get the list of categorized attributes related to the product.
- **[availabilityDate](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_availabilityDate)**  
  Get the date when the part is used in the product or is made available for sale.
- **[catalogs](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_catalogs)**  
  Get the list of associated catalogs. Returns the name and id values only.
- **[configureDuringSale](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_configureDuringSale)**  
  Determines whether to allow or prevent configuration when a bundle is sold.
- **[description](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_description)**  
  Get the description of the product. If data translation is set up and specified in the org, the translated description is available.
- **[discontinuedDate](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_discontinuedDate)**  
  Get the date from when the part can’t be used in the product or sold.
- **[displayUrl](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_displayUrl)**  
  Get the display image URL of the product.
- **[endOfLifeDate](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_endOfLifeDate)**  
  Get the date after which a product isn’t supported, ordered, or maintained.
- **[id](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_id)**  
  Get the ID of the product.
- **[isActive](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isActive)**  
  Indicates whether the product is active (true) or not (false).
- **[isAssetizable](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isAssetizable)**  
  Indicates whether the product instance remains a customer asset after it's purchased (true) or not (false).
- **[isComponentRequired](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isComponentRequired)**  
  Indicates whether the product component is required (true) or not (false).
- **[isDefaultComponent](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isDefaultComponent)**  
  Indicates whether the product component is the default component (true) or not (false).
- **[isQuantityEditable](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isQuantityEditable)**  
  Indicates whether the product quantity is editable (true) or not (false).
- **[isSoldOnlyWithOtherProds](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_isSoldOnlyWithOtherProds)**  
  Indicates whether the product can't be sold separately (true) or not (false).
- **[name](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_name)**  
  Get the name of the product. If data translation is set up and specified in the org, the translated name is available.
- **[nodeType](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_nodeType)**  
  Get the type of the node, such as a product or bundled product.
- **[productClassification](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productClassification)**  
  Get the details of the product classification that the product is based on.
- **[productCode](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productCode)**  
  Get the universal product code that's used to track the part that’s used in the product.
- **[productComponentGroups](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productComponentGroups)**  
  Get the logical grouping of the component products in a bundle and group cardinality for ordering the product components.
- **[productInformation](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productInformation)**  
  Get the details of a product.
- **[productPricingInformation](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productPricingInformation)**  
  Get the pricing details of a product.
- **[productQuantity](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productQuantity)**  
  Get the quantity of a product.
- **[productRelatedComponent](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productRelatedComponent)**  
  Get the details of the related components of a product.
- **[productSellingModelOptions](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productSellingModelOptions)**  
  Get the details of the product selling model options.
- **[productSpecificationType](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productSpecificationType)**  
  Get the details of the product specification type.
- **[productType](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_productType)**  
  Get the product type.
- **[qualificationContext](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_qualificationContext)**  
  Get the context details of a user, which are used for qualification rules.
- **[status](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md#apex_runtime_industries_cpq_ProductOutputRepresentation_status)**  
  Get or set the status of the product, such as Active or Inactive.

### additionalFields

Get the key-value pair of additional standard or custom fields with their
values.

#### Signature

`public List<runtime_industries_cpq.AdditionalFieldsWrapper> additionalFields {get; set;}`

#### Property Value

Type: List<runtime\_industries\_cpq.AdditionalFieldsWrapper>

### attributeCategories

Get the list of categorized attributes related to the product.

#### Signature

`public List<runtime_industries_cpq.AttributeCategoryOutputRepresentation> attributeCategories {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.AttributeCategoryOutputRepresentation](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation "Stores details of an attribute such as code, description, usage type, and so on.")>

### availabilityDate

Get the date when the part is used in the product or is made available for
sale.

#### Signature

`public Datetime availabilityDate {get; set;}`

#### Property Value

Type: Datetime

### catalogs

Get the list of associated catalogs. Returns the name and id values only.

#### Signature

`public List<runtime_industries_cpq.CatalogOutputRepresentation> catalogs {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.CatalogOutputRepresentation](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_CatalogOutputRepresentation "Contains properties to store details of a catalog definition.")>

### configureDuringSale

Determines whether to allow or prevent configuration when a bundle is sold.

#### Signature

`public String configureDuringSale {get; set;}`

#### Property Value

Type: String

### description

Get the description of the product. If data translation is set up and specified in the
org, the translated description is available.

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

Indicates whether the product instance remains a customer asset after it's purchased
(true) or not (false).

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

Indicates whether the product component is the default component (true) or not
(false).

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

Indicates whether the product can't be sold separately (true) or not (false).

#### Signature

`public Boolean isSoldOnlyWithOtherProds {get; set;}`

#### Property Value

Type: Boolean

### name

Get the name of the product. If data translation is set up and specified in the org, the
translated name is available.

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

### productClassification

Get the details of the product classification that the product is based on.

#### Signature

`public runtime_industries_cpq.ProductClassificationOutputRepresentation productClassification {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductClassificationOutputRepresentation](./apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation "Get details of the product classification in a product configuration.")

### productCode

Get the universal product code that's used to track the part that’s used in the
product.

#### Signature

`public String productCode {get; set;}`

#### Property Value

Type: String

### productComponentGroups

Get the logical grouping of the component products in a bundle and group cardinality for
ordering the product components.

#### Signature

`public List<runtime_industries_cpq.ProductComponentGroupOutputRepresentation> productComponentGroups {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.ProductComponentGroupOutputRepresentation](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation "Get details of the product component group in a product classification.")>

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

Type: [runtime\_industries\_cpq.ProductQuantityOutputRepresentation](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation "Represents the quantity constraints and current quantity for a product in the product discovery context.")

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

Type: List<[runtime\_industries\_cpq.ProductSellingModelOptionOutputRepresentation](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation "Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).")>

### productSpecificationType

Get the details of the product specification type.

#### Signature

`public runtime_industries_cpq.ProductSpecificationTypeOutputRepresentation productSpecificationType {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.ProductSpecificationTypeOutputRepresentation](./apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation "Represents a product specification type that defines the structure and attributes available for configuring a product.")

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

Type: [runtime\_industries\_cpq.QualificationContextOutputRepresentation](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation "Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.")

### status

Get or set the status of the product, such as Active or Inactive.

#### Signature

`public String status {get; set;}`

#### Property Value

Type: String
