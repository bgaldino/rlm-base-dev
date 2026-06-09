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

- **[AdditionalContextData Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalContextData.htm)**  
  Contains properties to include a list of additional context data nodes. These nodes are used along with the context definition nodes for data hydration.
- **[AdditionalFields Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalFields.htm)**  
  Contains properties to include a map where the key is a string and the value is an instance of the AdditionalFieldsInput class.
- **[AdditionalFieldsInput Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalFieldsInput.htm)**  
  Contains properties to include the additional standard or custom fields in the request.
- **[ApiStatusRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ApiStatusRepresentation.htm)**  
  Stores details of the API request such as execution messages, status code, and status message.
- **[AttributeCategoryOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributeCategoryOutputRepresentation.htm)**  
  Stores details of an attribute such as code, description, usage type, and so on.
- **[AttributePickListOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributePickListOutputRepresentation.htm)**  
  Stores details of an attribute picklist.
- **[AttributePickListValueOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AttributePickListValueOutputRepresentation.htm)**  
  Stores details of an attribute picklist value.
- **[BulkProductDetailsInputBody Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBody.htm)**  
  Contains the details of the request to retrieve product details by using product ID and product selling model ID.
- **[BulkProductDetailsInputBodyList Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsInputBodyList.htm)**  
  Contains details of the request to retrieve a list of products.
- **[BulkProductDetailsRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_BulkProductDetailsRepresentation.htm)**  
  Get the details of multiple product definitions in a single request. This class is used for bulk product retrieval operations in Product Discovery.
- **[CatalogOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_CatalogOutputRepresentation.htm)**  
  Contains properties to store details of a catalog definition.
- **[ConfigRuleResult Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ConfigRuleResult.htm)**  
  Contains the results of configuration rule evaluation, including message rules, product recommendation rules, and visibility rules that are applied during product configuration.
- **[CategoryOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm)**  
  Contains properties to store details of a category.
- **[ContextDataInput Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ContextDataInput.htm)**  
  Get details of a context.
- **[FacetValueRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FacetValueRepresentation.htm)**  
  Get details of the facet values that are found in the search result.
- **[Filter Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_Filter.htm)**  
  Contains the criteria property to store the details of a filter criteria, which is used to filter records.
- **[FilterCriteriaInputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm)**  
  Contains properties to store criteria details to filter records based on supported properties.
- **[FilterInputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterInputRepresentation.htm)**  
  Contains the filter property to filters records based on supported criteria.
- **[GuidedSelectionRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_GuidedSelectionRepresentation.htm)**  
  Contains properties to represent a product in a guided selection flow. This class is used in Product Discovery to provide structured product information during guided product selection processes.
- **[GuidedSelectionSearchTerm Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_GuidedSelectionSearchTerm.htm)**  
  Represents a search term used in guided product selection. Contains the search term text and associated tags for filtering and searching products in Product Discovery.
- **[GuidedSelectionSearchTermList Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_GuidedSelectionSearchTermList.htm)**  
  Contains a list of search terms used in guided product selection. This class is used to pass multiple search terms for filtering and searching products in Product Discovery.
- **[MessageRule Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_MessageRule.htm)**  
  Represents a message rule that is evaluated during product configuration. Message rules display informational, warning, or error messages to users based on configuration conditions.
- **[PricingModelOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_PricingModelOutputRepresentation.htm)**  
  Contains details of a pricing model in a product configuration.
- **[ProductAttributeOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductAttributeOutputRepresentation.htm)**  
  Contains details about the attribute in a product configuration.
- **[ProductClassificationOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductClassificationOutputRepresentation.htm)**  
  Get details of the product classification in a product configuration.
- **[ProductComponentGroupOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductComponentGroupOutputRepresentation.htm)**  
  Get details of the product component group in a product classification.
- **[ProductComponentGroupRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductComponentGroupRepresentation.htm)**  
  Represents a product component group used in bulk product operations. This class is similar to ProductComponentGroupOutputRepresentation but is used specifically for bulk product detail representations where components are represented as BulkProductDetailsRepresentation objects.
- **[ProductDetailsRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductDetailsRepresentation.htm)**  
  Get the details of a product definition.
- **[ProductListRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductListRepresentation.htm)**  
  Get the list of retrieved products.
- **[ProductOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductOutputRepresentation.htm)**  
  Get the details of a product definition.
- **[ProductPricesOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductPricesOutputRepresentation.htm)**  
  Get the price details of a product.
- **[ProductQuantityOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductQuantityOutputRepresentation.htm)**  
  Represents the quantity constraints and current quantity for a product in the product discovery context.
- **[ProductRecommendationRule Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductRecommendationRule.htm)**  
  Represents a product recommendation rule that is evaluated during product configuration. Product recommendation rules suggest additional products to users based on configuration conditions.
- **[ProductRelatedComponentOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductRelatedComponentOutputRepresentation.htm)**  
  Represents a related component product in a bundle or product relationship, including component configuration details such as quantity constraints, required status, and relationship metadata.
- **[ProductSellingModelOptionOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSellingModelOptionOutputRepresentation.htm)**  
  Represents a selling model option available for a product, which defines how the product can be sold (such as subscription, one-time, or usage-based).
- **[ProductSellingModelOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSellingModelOutputRepresentation.htm)**  
  Represents a product selling model that defines how a product is sold, including the selling model type, pricing term, and status.
- **[ProductSpecificationRecordTypeOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSpecificationRecordTypeOutputRepresentation.htm)**  
  Represents the record type information for a product specification, which defines the type of record used to store product specification data.
- **[ProductSpecificationTypeOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_ProductSpecificationTypeOutputRepresentation.htm)**  
  Represents a product specification type that defines the structure and attributes available for configuring a product.
- **[QocQualificationOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_QocQualificationOutputRepresentation.htm)**  
  Represents a quote, order, or contract qualification that determines whether a product can be sold based on specific business rules and conditions.
- **[QualificationContextOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm)**  
  Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.
- **[RelatedObjectFilter Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_RelatedObjectFilter.htm)**  
  Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.
- **[RelatedObjectFilterInputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_RelatedObjectFilterInputRepresentation.htm)**  
  Represents input criteria for filtering products based on related object information, such as account, opportunity, or contract data.
- **[SearchProductsFacetRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm)**  
  Represents a search facet that provides filtering and categorization options for product search results, such as categories, attributes, or other product characteristics.
- **[SearchProductsRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_SearchProductsRepresentation.htm)**  
  Represents the results of a product search operation, including the list of products, search facets, pagination information, and total count of matching products.
- **[UnitOfMeasureOutputRepresentation Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_UnitOfMeasureOutputRepresentation.htm)**  
  Represents the unit of measure for a product. This class contains information about how product quantities are measured, including the unit code, name, scale, and rounding method.
- **[VisibilityRule Class](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_VisibilityRule.htm)**  
  Represents a visibility rule that is evaluated during product configuration. Visibility rules control the visibility of products, attributes, or other UI elements based on configuration conditions.
