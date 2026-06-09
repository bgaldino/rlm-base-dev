---
page_id: apex_namespace_runtime_industries_cpq.htm
title: runtime_industries_cpq Namespace
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_namespace_runtime_industries_cpq.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_apex_reference.htm
fetched_at: 2026-06-09
---

# runtime\_industries\_cpq Namespace

The runtime\_industries\_cpq namespace provides classes and methods to search products or
to manage products, catalogs, and categories.

The `runtime_industries_cpq` namespace includes these
classes.

## Usage

You can access the `runtime_industries_cpq` classes if
your org has the Product Discovery feature.

- **[AdditionalContextData Class](./apex_class_runtime_industries_cpq_AdditionalContextData.htm.md)**  
  Contains properties to include a list of additional context data nodes. These nodes are used along with the context definition nodes for data hydration.
- **[AdditionalFields Class](./apex_class_runtime_industries_cpq_AdditionalFields.htm.md)**  
  Contains properties to include a map where the key is a string and the value is an instance of the AdditionalFieldsInput class.
- **[AdditionalFieldsInput Class](./apex_class_runtime_industries_cpq_AdditionalFieldsInput.htm.md)**  
  Contains properties to include the additional standard or custom fields in the request.
- **[ApiStatusRepresentation Class](./apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm.md)**  
  Stores details of the API request such as execution messages, status code, and status message.
- **[AttributeCategoryOutputRepresentation Class](./apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm.md)**  
  Stores details of an attribute such as code, description, usage type, and so on.
- **[AttributePickListOutputRepresentation Class](./apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm.md)**  
  Stores details of an attribute picklist.
- **[AttributePickListValueOutputRepresentation Class](./apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation.htm.md)**  
  Stores details of an attribute picklist value.
- **[BulkProductDetailsInputBody Class](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm.md)**  
  Contains the details of the request to retrieve product details by using product ID and product selling model ID.
- **[BulkProductDetailsInputBodyList Class](./apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm.md)**  
  Contains details of the request to retrieve a list of products.
- **[BulkProductDetailsRepresentation Class](./apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm.md)**  
  Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.
- **[CatalogOutputRepresentation Class](./apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm.md)**  
  Contains properties to store details of a catalog definition.
- **[ConfigRuleResult Class](./apex_class_runtime_industries_cpq_ConfigRuleResult.htm.md)**  
  Contains the results of configuration rule evaluation, including message rules, product recommendation rules, and visibility rules that are applied during product configuration.
- **[CategoryOutputRepresentation Class](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md)**  
  Contains properties to store details of a category.
- **[ContextDataInput Class](./apex_class_runtime_industries_cpq_ContextDataInput.htm.md)**  
  Get details of a context.
- **[FacetValueRepresentation Class](./apex_class_runtime_industries_cpq_FacetValueRepresentation.htm.md)**  
  Get details of the facet values that are found in the search result.
- **[Filter Class](./apex_class_runtime_industries_cpq_Filter.htm.md)**  
  Contains the criteria property to store the details of a filter criteria, which is used to filter records.
- **[FilterCriteriaInputRepresentation Class](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md)**  
  Contains properties to store criteria details to filter records based on supported properties.
- **[FilterInputRepresentation Class](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md)**  
  Contains the filter property to filters records based on supported criteria.
- **[GuidedSelectionRepresentation Class](./apex_class_runtime_industries_cpq_GuidedSelectionRepresentation.htm.md)**  
  Contains properties to represent a product in a guided selection flow. This class is used in Product Discovery to provide structured product information during guided product selection processes.
- **[GuidedSelectionSearchTerm Class](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm.md)**  
  Represents a search term used in guided product selection. Contains the search term text and associated tags for filtering and searching products in Product Discovery.
- **[GuidedSelectionSearchTermList Class](./apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm.md)**  
  Contains a list of search terms used in guided product selection. This class is used to pass multiple search terms for filtering and searching products in Product Discovery.
- **[MessageRule Class](./apex_class_runtime_industries_cpq_MessageRule.htm.md)**  
  Represents a message rule that is evaluated during product configuration. Message rules display informational, warning, or error messages to users based on configuration conditions.
- **[PricingModelOutputRepresentation Class](./apex_class_runtime_industries_cpq_PricingModelOutputRepresentation.htm.md)**  
  Contains details of a pricing model in a product configuration.
- **[ProductAttributeOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation.htm.md)**  
  Contains details about the attribute in a product configuration.
- **[ProductClassificationOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm.md)**  
  Get details of the product classification in a product configuration.
- **[ProductComponentGroupOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm.md)**  
  Get details of the product component group in a product classification.
- **[ProductComponentGroupRepresentation Class](./apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm.md)**  
  Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.
- **[ProductDetailsRepresentation Class](./apex_class_runtime_industries_cpq_ProductDetailsRepresentation.htm.md)**  
  Get the details of a product definition.
- **[ProductListRepresentation Class](./apex_class_runtime_industries_cpq_ProductListRepresentation.htm.md)**  
  Get the list of retrieved products.
- **[ProductOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm.md)**  
  Get the details of a product definition.
- **[ProductPricesOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm.md)**  
  Get the price details of a product.
- **[ProductQuantityOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm.md)**  
  Represents the quantity constraints and current quantity for a product in the product discovery context.
- **[ProductRecommendationRule Class](./apex_class_runtime_industries_cpq_ProductRecommendationRule.htm.md)**  
  Represents a product recommendation rule that is evaluated during product configuration. Product recommendation rules suggest additional products to users based on configuration conditions.
- **[ProductRelatedComponentOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm.md)**  
  Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.
- **[ProductSellingModelOptionOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm.md)**  
  Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).
- **[ProductSellingModelOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm.md)**  
  Represents a product selling model that defines how a product is sold, including the selling model type, pricing term, and status.
- **[ProductSpecificationRecordTypeOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductSpecificationRecordTypeOutputRepresentation.htm.md)**  
  Represents the record type information for a product specification, which defines the type of record used to store product specification data.
- **[ProductSpecificationTypeOutputRepresentation Class](./apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm.md)**  
  Represents a product specification type that defines the structure and attributes available for configuring a product.
- **[QocQualificationOutputRepresentation Class](./apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm.md)**  
  Represents a quote, order, or contract qualification that determines whether a product can be sold based on specific business rules and conditions.
- **[QualificationContextOutputRepresentation Class](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md)**  
  Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.
- **[RelatedObjectFilter Class](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md)**  
  Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.
- **[RelatedObjectFilterInputRepresentation Class](./apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm.md)**  
  Represents input criteria for filtering products based on related object information, such as account, opportunity, or contract data.
- **[SearchProductsFacetRepresentation Class](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md)**  
  Represents a search facet that provides filtering and categorization options for product search results, such as categories, attributes, or other product characteristics.
- **[SearchProductsRepresentation Class](./apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm.md)**  
  Represents the results of a product search operation, including the list of products, search facets, pagination information, and total count of matching products.
- **[UnitOfMeasureOutputRepresentation Class](./apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm.md)**  
  Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.
- **[VisibilityRule Class](./apex_class_runtime_industries_cpq_VisibilityRule.htm.md)**  
  Represents a visibility rule that is evaluated during product configuration. Visibility rules control the visibility of products, attributes, or other UI elements based on configuration conditions.
