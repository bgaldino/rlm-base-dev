---
page_id: apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm
title: CategoryOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# CategoryOutputRepresentation Class

Contains properties to store details of a category.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[CategoryOutputRepresentation Properties](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_properties)**  
  Learn more about the properties available with the CategoryOutputRepresentation class.

## CategoryOutputRepresentation Properties

Learn more about the properties available with the CategoryOutputRepresentation
class.

The `CategoryOutputRepresentation` class includes these
properties.

- **[catalogId](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_catalogId)**  
  Get the ID of the catalog that the category is associated with.
- **[description](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_description)**  
  Get the description of a catalog.
- **[hasSubCategories](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_hasSubCategories)**  
  Indicates whether the subcategories are available (true) or not (false).
- **[id](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_id)**  
  Get the ID of the category.
- **[isNavigational](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_isNavigational)**  
  Indicates whether the category node is navigational (true) or not (false).
- **[name](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_name)**  
  Get the name of the category. If data translation is set up and specified in the org, the translated name is available.
- **[parentCategoryId](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_parentCategoryId)**  
  Get the ID of the parent category.
- **[qualificationContext](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_qualificationContext)**  
  Get the context details of a user, which are used for qualification rules.
- **[sortOrder](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_sortOrder)**  
  Get the display order of the product category relative to the siblings with the same parent category.
- **[childCategories](./apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm.md#apex_runtime_industries_cpq_CategoryOutputRepresentation_childCategories)**  
  Get the list of childcategorie.

### catalogId

Get the ID of the catalog that the category is associated with.

#### Signature

`public String catalogId {get; set;}`

#### Property Value

Type: String

### description

Get the description of a catalog.

#### Signature

`public String description {get; set;}`

#### Property Value

Type: String

### hasSubCategories

Indicates whether the subcategories are available (true) or not (false).

#### Signature

`public Boolean hasSubCategories {get; set;}`

#### Property Value

Type: Boolean

### id

Get the ID of the category.

#### Signature

`public String id {get; set;}`

#### Property Value

Type: String

### isNavigational

Indicates whether the category node is navigational (true) or not (false).

#### Signature

`public Boolean isNavigational {get; set;}`

#### Property Value

Type: Boolean

### name

Get the name of the category. If data translation is set up and specified in the org, the
translated name is available.

#### Signature

`public String name {get; set;}`

#### Property Value

Type: String

### parentCategoryId

Get the ID of the parent category.

#### Signature

`public String parentCategoryId {get; set;}`

#### Property Value

Type: String

### qualificationContext

Get the context details of a user, which are used for qualification rules.

#### Signature

`public runtime_industries_cpq.QualificationContextOutputRepresentation qualificationContext {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.QualificationContextOutputRepresentation](./apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation.htm.md#apex_class_runtime_industries_cpq_QualificationContextOutputRepresentation "Represents the context information used for product qualification, including account, opportunity, and other relevant context data for determining product eligibility.")

### sortOrder

Get the display order of the product category relative to the siblings with the same
parent category.

#### Signature

`public Integer sortOrder {get; set;}`

#### Property Value

Type: Integer

### childCategories

Get the list of childcategorie.

#### Signature

`public List<runtime_industries_cpq.CategoryOutputRepresentation> childCategories {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.CategoryOutputRepresentation](#apex_class_runtime_industries_cpq_CategoryOutputRepresentation "Contains properties to store details of a category.")>
