---
article_id: release-notes.rn_runtime_industries_cpq_namespace.htm
title: runtime_industries_cpq Namespace
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_runtime_industries_cpq_namespace.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_catalog_management.htm
fetched_at: 2026-09-30
---

# runtime_industries_cpq Namespace

Work with product variations and units of measure during product discovery and selection. The runtime_industries_cpq namespace includes new classes and properties that represent a product's variation attributes, variation class, child variations, and units of measure.

New Classes
Get the details of a product's variation attribute set
Use the new ProductVariantAttributeSetOutputRepresentation class constructors and properties.
Get the details of a variation attribute in a product's variation attribute set
Use the new ProductVariantAttributeOutputRepresentation class constructors and properties.
Get the details of a variation attribute value
Use the new ProductVariantAttributeValueOutputRepresentation class constructors and properties.
Get the details of a product's unit of measure
Use the new ProductUnitOfMeasureOutputRepresentation class constructor and properties.
New Properties in Existing Classes
Get the variation class of a product

Use the new productClass property in the existing ProductDetailsRepresentation, ProductOutputRepresentation, ProductListRepresentation, BulkProductDetailsRepresentation, SearchProductsRepresentation, and GuidedSelectionRepresentation classes.

Get the child variations of a product

Use the new childVariationIds property in the existing ProductDetailsRepresentation, ProductOutputRepresentation, ProductListRepresentation, BulkProductDetailsRepresentation, SearchProductsRepresentation, and GuidedSelectionRepresentation classes.

Get the variation attribute set of a product

Use the new variationAttributeSet property in the existing ProductDetailsRepresentation, ProductOutputRepresentation, ProductListRepresentation, BulkProductDetailsRepresentation, SearchProductsRepresentation, and GuidedSelectionRepresentation classes.

Get the number of variations for a product

Use the new variationsCount property in the existing ProductListRepresentation, SearchProductsRepresentation, and GuidedSelectionRepresentation classes.

Get the categories of a product

Use the new productCategories property in the existing SearchProductsRepresentation class.

Get the sequence of an attribute category

Use the new sequence property in the existing AttributeCategoryOutputRepresentation class.

Get the units of measure for a product

Use the new productUnitOfMeasures property in the existing ProductDetailsRepresentation, ProductListRepresentation, BulkProductDetailsRepresentation, SearchProductsRepresentation, and GuidedSelectionRepresentation classes.

SEE ALSO
Revenue Management Developer Guide: Product Discovery Apex Reference
