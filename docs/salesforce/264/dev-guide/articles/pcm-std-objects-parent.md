---
page_id: pcm-std-objects-parent
title: Product Catalog Management Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/pcm-std-objects-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: pcm-overview
legacy_page_id: pcm_std_objects_parent.htm
fetched_at: 2026-11-25
---

# Product Catalog Management Standard Objects

The Product Catalog Management data model provides objects and fields to manage products, rules, and catalogs.

- 

**[AttributeCategory](./sforce-api-objects-attributecategory.md)**

Represents a logical grouping of attributes that can be reused while defining products. Attribute Categories are used for searching and managing product attributes. For example, the “Mobile Handset Properties” category has color, storage and make model, and size attributes. This object is available in API version 60.0 and later.

- 

**[AttributeCategoryAttribute](./sforce-api-objects-attributecategoryattribute.md)**

Represents a relationship between an attribute category and the attribute definition. This object is available in API version 60.0 and later.

- 

**[AttrPicklistExcludedValue](./sforce-api-objects-attrpicklistexcludedvalue.md)**

Represents the excluded picklist values for a product classification attribute or a product attribute definition. This object is available in API version 61.0 and later.

- 

**[ProductAttributeDefinition](./sforce-api-objects-productattributedefinition.md)**

Represents the relationship between a product and its attributes. This object is available in API version 60.0 and later.

- 

**[ProductCategoryDisqual](./sforce-api-objects-productcategorydisqual.md)**

Represents disqualification rules for product categories. The rules determine when the product category doesn’t qualify to be displayed to users. This object is available in API version 60.0 and later.

- 

**[ProductCategoryQualification](./sforce-api-objects-productcategoryqualification.md)**

Represents qualification rules for product categories. The rules determine when the product category qualifies to be displayed to users. This object is available in API version 60.0 and later.

- 

**[ProductClassification](./sforce-api-objects-productclassification.md)**

Represents a template that holds a collection of dynamic attributes. Product classification is used to quickly define and create multiple products that are similar yet different. This object is available in API version 60.0 and later.

- 

**[ProductClassificationAttr](./sforce-api-objects-productclassificationattr.md)**

Represents the relationship between a product classification and its attributes. This is the default configuration for products based on the product classification. This object is available in API version 60.0 and later.

- 

**[ProductComponentGrpOverride](./sforce-api-objects-productcomponentgrpoverride.md)**

Represents override information for a Product Component Group. The cardinality of the product component group can be overridden in the context of a product bundle. This object is available in API version 60.0 and later.

- 

**[ProductDisqualification](./sforce-api-objects-productdisqualification.md)**

Represents disqualification rules for products. The rules determine when the product doesn’t qualify to be displayed to users. The rules are based on user context. This object is available in API version 60.0 and later.

- 

**[ProductQualification](./sforce-api-objects-productqualification.md)**

Represents qualification rules for products. The rules determine when the product qualifies to be displayed to users. The rules are based on user context. This object is available in API version 60.0 and later.

- 

**[ProductRampSegment](./sforce-api-objects-productrampsegment.md)**

Represents the ramp period within a ramp deal where terms, volumes, and other commitments change over time. This object is available in API version 62.0 and later.

- 

**[ProductRelComponentOverride](./sforce-api-objects-productrelcomponentoverride.md)**

Represents the cardinality overrides for product components in a bundle. This object is available in API version 60.0 and later.

- 

**[ProductSpecificationRecType](./sforce-api-objects-productspecificationrectype.md)**

Represents the relationship between industry-specific product specifications and the product record type. This object is available in API version 60.0 and later.

- 

**[ProductSpecificationType](./sforce-api-objects-productspecificationtype.md)**

Represents the type of product specification provided by the user to make the product terminology unique to an industry. A product specification type is associated with a product specification record type. This object is available in API version 60.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/pcm-std-objects-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
