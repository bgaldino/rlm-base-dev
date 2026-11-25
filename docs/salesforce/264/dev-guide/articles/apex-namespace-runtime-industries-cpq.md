---
page_id: apex-namespace-runtime-industries-cpq
title: runtime_industries_cpq Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-runtime-industries-cpq.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-discovery-apex-reference
legacy_page_id: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-11-25
---

# runtime_industries_cpq Namespace

The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.

The `runtime_industries_cpq` namespace includes these classes.

## Usage

You can access the `runtime_industries_cpq` classes if your org has the Product Discovery feature.

- 

**[AdditionalContextData Class](./apex-class-runtime-industries-cpq-additionalcontextdata.md#additionalcontextdata-class)**

Contains properties to include a list of additional context data nodes. These nodes are used along with the context definition nodes for data hydration.

- 

**[AdditionalFields Class](./apex-class-runtime-industries-cpq-additionalfields.md#additionalfields-class)**

Contains properties to include a map where the key is a string and the value is an instance of the AdditionalFieldsInput class.

- 

**[AdditionalFieldsInput Class](./apex-class-runtime-industries-cpq-additionalfieldsinput.md#additionalfieldsinput-class)**

Contains properties to include the additional standard or custom fields in the request.

- 

**[ApiStatusRepresentation Class](./apex-class-runtime-industries-cpq-apistatusrepresentation.md#apistatusrepresentation-class)**

Stores details of the API request such as execution messages, status code, and status message.

- 

**[AttributeCategoryOutputRepresentation Class](./apex-class-runtime-industries-cpq-attributecategoryoutputrepresentation.md#attributecategoryoutputrepresentation-class)**

Stores details of an attribute such as code, description, usage type, and so on.

- 

**[AttributePickListOutputRepresentation Class](./apex-class-runtime-industries-cpq-attributepicklistoutputrepresentation.md#attributepicklistoutputrepresentation-class)**

Stores details of an attribute picklist.

- 

**[AttributePickListValueOutputRepresentation Class](./apex-class-runtime-industries-cpq-attributepicklistvalueoutputrepresentation.md#attributepicklistvalueoutputrepresentation-class)**

Stores details of an attribute picklist value.

- 

**[BulkProductDetailsInputBody Class](./apex-class-runtime-industries-cpq-bulkproductdetailsinputbody.md#bulkproductdetailsinputbody-class)**

Contains the details of the request to retrieve product details by using product ID and product selling model ID.

- 

**[BulkProductDetailsInputBodyList Class](./apex-class-runtime-industries-cpq-bulkproductdetailsinputbodylist.md#bulkproductdetailsinputbodylist-class)**

Contains details of the request to retrieve a list of products.

- 

**[BulkProductDetailsRepresentation Class](./apex-class-runtime-industries-cpq-bulkproductdetailsrepresentation.md#bulkproductdetailsrepresentation-class)**

Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.

- 

**[CatalogOutputRepresentation Class](./apex-class-runtime-industries-cpq-catalogoutputrepresentation.md#catalogoutputrepresentation-class)**

Contains properties to store details of a catalog definition.

- 

**[ConfigRuleResult Class](./apex-class-runtime-industries-cpq-configruleresult.md#configruleresult-class)**

Contains the results of configuration rule evaluation, including message rules, product recommendation rules, and visibility rules that are applied during product configuration.

- 

**[CategoryOutputRepresentation Class](./apex-class-runtime-industries-cpq-categoryoutputrepresentation.md#categoryoutputrepresentation-class)**

Contains properties to store details of a category.

- 

**[ContextDataInput Class](./apex-class-runtime-industries-cpq-contextdatainput.md#contextdatainput-class)**

Get details of a context.

- 

**[FacetValueRepresentation Class](./apex-class-runtime-industries-cpq-facetvaluerepresentation.md#facetvaluerepresentation-class)**

Get details of the facet values that are found in the search result.

- 

**[Filter Class](./apex-class-runtime-industries-cpq-filter.md#filter-class)**

Contains the criteria property to store the details of a filter criteria, which is used to filter records.

- 

**[FilterCriteriaInputRepresentation Class](./apex-class-runtime-industries-cpq-filtercriteriainputrepresentation.md#filtercriteriainputrepresentation-class)**

Contains properties to store criteria details to filter records based on supported properties.

- 

**[FilterInputRepresentation Class](./apex-class-runtime-industries-cpq-filterinputrepresentation.md#filterinputrepresentation-class)**

Contains the filter property to filters records based on supported criteria.

- 

**[GuidedSelectionRepresentation Class](./apex-class-runtime-industries-cpq-guidedselectionrepresentation.md#guidedselectionrepresentation-class)**

Contains properties to represent a product in a guided selection flow. This class is used in Product Discovery to provide structured product information during guided product selection processes.

- 

**[GuidedSelectionSearchTerm Class](./apex-class-runtime-industries-cpq-guidedselectionsearchterm.md#guidedselectionsearchterm-class)**

Represents a search term used in guided product selection. Contains the search term text and associated tags for filtering and searching products in Product Discovery.

- 

**[GuidedSelectionSearchTermList Class](./apex-class-runtime-industries-cpq-guidedselectionsearchtermlist.md#guidedselectionsearchtermlist-class)**

Contains a list of search terms used in guided product selection. This class is used to pass multiple search terms for filtering and searching products in Product Discovery.

- 

**[MessageRule Class](./apex-class-runtime-industries-cpq-messagerule.md#messagerule-class)**

Represents a message rule that is evaluated during product configuration. Message rules display informational, warning, or error messages to users based on configuration conditions.

- 

**[PricingModelOutputRepresentation Class](./apex-class-runtime-industries-cpq-pricingmodeloutputrepresentation.md#pricingmodeloutputrepresentation-class)**

Contains details of a pricing model in a product configuration.

- 

**[ProductAttributeOutputRepresentation Class](./apex-class-runtime-industries-cpq-productattributeoutputrepresentation.md#productattributeoutputrepresentation-class)**

Contains details about the attribute in a product configuration.

- 

**[ProductClassificationOutputRepresentation Class](./apex-class-runtime-industries-cpq-productclassificationoutputrepresentation.md#productclassificationoutputrepresentation-class)**

Get details of the product classification in a product configuration.

- 

**[ProductComponentGroupOutputRepresentation Class](./apex-class-runtime-industries-cpq-productcomponentgroupoutputrepresentation.md#productcomponentgroupoutputrepresentation-class)**

Get details of the product component group in a product classification.

- 

**[ProductComponentGroupRepresentation Class](./apex-class-runtime-industries-cpq-productcomponentgrouprepresentation.md#productcomponentgrouprepresentation-class)**

Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.

- 

**[ProductDetailsRepresentation Class](./apex-class-runtime-industries-cpq-productdetailsrepresentation.md#productdetailsrepresentation-class)**

Get the details of a product definition.

- 

**[ProductListRepresentation Class](./apex-class-runtime-industries-cpq-productlistrepresentation.md#productlistrepresentation-class)**

Get the list of retrieved products.

- 

**[ProductOutputRepresentation Class](./apex-class-runtime-industries-cpq-productoutputrepresentation.md#productoutputrepresentation-class)**

Get the details of a product definition.

- 

**[ProductPricesOutputRepresentation Class](./apex-class-runtime-industries-cpq-productpricesoutputrepresentation.md#productpricesoutputrepresentation-class)**

Get the price details of a product.

- 

**[ProductQuantityOutputRepresentation Class](./apex-class-runtime-industries-cpq-productquantityoutputrepresentation.md#productquantityoutputrepresentation-class)**

Represents the quantity constraints and current quantity for a product in the product discovery context.

- 

**[ProductRecommendationRule Class](./apex-class-runtime-industries-cpq-productrecommendationrule.md#productrecommendationrule-class)**

Represents a product recommendation rule that is evaluated during product configuration. Product recommendation rules suggest additional products to users based on configuration conditions.

- 

**[ProductRelatedComponentOutputRepresentation Class](./apex-class-ricpq-productrelatedcomponentor.md#productrelatedcomponentoutputrepresentation-class)**

Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.

- 

**[ProductSellingModelOptionOutputRepresentation Class](./apex-class-ricpq-productsellingmodeloptionor.md#productsellingmodeloptionoutputrepresentation-class)**

Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).

- 

**[ProductSellingModelOutputRepresentation Class](./apex-class-runtime-industries-cpq-productsellingmodeloutputrepresentation.md#productsellingmodeloutputrepresentation-class)**

Represents a product selling model that defines how a product is sold, including the selling model type, pricing term, and status.

- 

**[ProductSpecificationRecordTypeOutputRepresentation Class](./apex-class-ricpq-productspecificationrecordtypeor.md#productspecificationrecordtypeoutputrepresentation-class)**

Represents the record type information for a product specification, which defines the type of record used to store product specification data.

- 

**[ProductSpecificationTypeOutputRepresentation Class](./apex-class-ricpq-productspecificationtypeor.md#productspecificationtypeoutputrepresentation-class)**

Represents a product specification type that defines the structure and attributes available for configuring a product.

- 

**[ProductUnitOfMeasureOutputRepresentation Class](./apex-class-runtime-industries-cpq-productunitofmeasureoutputrepresentation.md#productunitofmeasureoutputrepresentation-class)**

Represents a unit of measure that’s available for a product, including whether it’s the base or default unit and whether it’s orderable.

- 

**[ProductVariantAttributeOutputRepresentation Class](./apex-class-runtime-industries-cpq-productvariantattributeoutputrepresentation.md#productvariantattributeoutputrepresentation-class)**

Stores details of an attribute that defines a product variation, including the field and its label.

- 

**[ProductVariantAttributeSetOutputRepresentation Class](./apex-class-runtime-industries-cpq-productvariantattributesetoutputrepresentat.md#productvariantattributesetoutputrepresentation-class)**

Stores the set of attributes that define the variations of a product.

- 

**[ProductVariantAttributeValueOutputRepresentation Class](./apex-class-runtime-industries-cpq-productvariantattributevalueoutputrepresent.md#productvariantattributevalueoutputrepresentation-class)**

Stores the value of a product variation attribute.

- 

**[QocQualificationOutputRepresentation Class](./apex-class-runtime-industries-cpq-qocqualificationoutputrepresentation.md#qocqualificationoutputrepresentation-class)**

Represents a quote, order, or contract qualification that determines whether a product can be sold based on specific business rules and conditions.

- 

**[QualificationContextOutputRepresentation Class](./apex-class-runtime-industries-cpq-qualificationcontextoutputrepresentation.md#qualificationcontextoutputrepresentation-class)**

Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.

- 

**[RelatedObjectFilter Class](./apex-class-runtime-industries-cpq-relatedobjectfilter.md#relatedobjectfilter-class)**

Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.

- 

**[RelatedObjectFilterInputRepresentation Class](./apex-class-runtime-industries-cpq-relatedobjectfilterinputrepresentation.md#relatedobjectfilterinputrepresentation-class)**

Represents input criteria for filtering products based on related object information, such as account, opportunity, or contract data.

- 

**[SearchProductsFacetRepresentation Class](./apex-class-runtime-industries-cpq-searchproductsfacetrepresentation.md#searchproductsfacetrepresentation-class)**

Represents a search facet that provides filtering and categorization options for product search results, such as categories, attributes, or other product characteristics.

- 

**[SearchProductsRepresentation Class](./apex-class-runtime-industries-cpq-searchproductsrepresentation.md#searchproductsrepresentation-class)**

Represents the results of a product search operation, including the list of products, search facets, pagination information, and total count of matching products.

- 

**[UnitOfMeasureOutputRepresentation Class](./apex-class-runtime-industries-cpq-unitofmeasureoutputrepresentation.md#unitofmeasureoutputrepresentation-class)**

Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.

- 

**[VisibilityRule Class](./apex-class-runtime-industries-cpq-visibilityrule.md#visibilityrule-class)**

Represents a visibility rule that is evaluated during product configuration. Visibility rules control the visibility of products, attributes, or other UI elements based on configuration conditions.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-runtime-industries-cpq.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
