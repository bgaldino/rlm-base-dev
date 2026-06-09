---
page_id: pcm_std_objects_parent.htm
title: Product Catalog Management Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/pcm_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: pcm_overview.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Standard Objects

The Product Catalog Management data model provides objects and fields to manage
products, rules, and catalogs.

- **[AttributeCategory](./sforce_api_objects_attributecategory.htm.md)**  
  Represents a logical grouping of attributes that can be reused while defining products. Attribute Categories are used for searching and managing product attributes. For example, the "Mobile Handset Properties" category has color, storage and make model, and size attributes. This object is available in API version 60.0 and later.
- **[AttributeCategoryAttribute](./sforce_api_objects_attributecategoryattribute.htm.md)**  
  Represents a relationship between an attribute category and the attribute definition. This object is available in API version 60.0 and later.
- **[AttrPicklistExcludedValue](./sforce_api_objects_attrpicklistexcludedvalue.htm.md)**  
  Represents the excluded picklist values for a product classification attribute or a product attribute definition. This object is available in API version 61.0 and later.
- **[ProductAttributeDefinition](./sforce_api_objects_productattributedefinition.htm.md)**  
  Represents the relationship between a product and its attributes. This object is available in API version 60.0 and later.
- **[ProductCategoryDisqual](./sforce_api_objects_productcategorydisqual.htm.md)**  
  Represents disqualification rules for product categories. The rules determine when the product category doesn’t qualify to be displayed to users. This object is available in API version 60.0 and later.
- **[ProductCategoryQualification](./sforce_api_objects_productcategoryqualification.htm.md)**  
  Represents qualification rules for product categories. The rules determine when the product category qualifies to be displayed to users. This object is available in API version 60.0 and later.
- **[ProductClassification](./sforce_api_objects_productclassification.htm.md)**  
  Represents a template that holds a collection of dynamic attributes. Product classification is used to quickly define and create multiple products that are similar yet different. This object is available in API version 60.0 and later.
- **[ProductClassificationAttr](./sforce_api_objects_productclassificationattr.htm.md)**  
  Represents the relationship between a product classification and its attributes. This is the default configuration for products based on the product classification. This object is available in API version 60.0 and later.
- **[ProductComponentGrpOverride](./sforce_api_objects_productcomponentgrpoverride.htm.md)**  
  Represents override information for a Product Component Group. The cardinality of the product component group can be overridden in the context of a product bundle. This object is available in API version 60.0 and later.
- **[ProductDisqualification](./sforce_api_objects_productdisqualification.htm.md)**  
  Represents disqualification rules for products. The rules determine when the product doesn’t qualify to be displayed to users. The rules are based on user context. This object is available in API version 60.0 and later.
- **[ProductQualification](./sforce_api_objects_productqualification.htm.md)**  
  Represents qualification rules for products. The rules determine when the product qualifies to be displayed to users. The rules are based on user context. This object is available in API version 60.0 and later.
- **[ProductRampSegment](./sforce_api_objects_productrampsegment.htm.md)**  
  Represents the ramp period within a ramp deal where terms, volumes, and other commitments change over time. This object is available in API version 62.0 and later.
- **[ProductRelComponentOverride](./sforce_api_objects_productrelcomponentoverride.htm.md)**  
  Represents the cardinality overrides for product components in a bundle. This object is available in API version 60.0 and later.
- **[ProductSpecificationRecType](./sforce_api_objects_productspecificationrectype.htm.md)**  
  Represents the relationship between industry-specific product specifications and the product record type. This object is available in API version 60.0 and later.
- **[ProductSpecificationType](./sforce_api_objects_productspecificationtype.htm.md)**  
  Represents the type of product specification provided by the user to make the product terminology unique to an industry. A product specification type is associated with a product specification record type. This object is available in API version 60.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects and Fields
         - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
