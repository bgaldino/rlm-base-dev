---
page_id: apex-class-runtime-industries-cpq-categoryoutputrepresentation
title: CategoryOutputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-categoryoutputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_CategoryOutputRepresentation.htm
fetched_at: 2026-11-25
---

# CategoryOutputRepresentation Class

Contains properties to store details of a category.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[CategoryOutputRepresentation Properties](#categoryoutputrepresentation-properties)**

Learn more about the properties available with the CategoryOutputRepresentation class.

## CategoryOutputRepresentation Properties

Learn more about the properties available with the CategoryOutputRepresentation class.

The `CategoryOutputRepresentation` class includes these properties.

- 

**[catalogId](#catalogid)**

Get the ID of the catalog that the category is associated with.

- 

**[description](#description)**

Get the description of a catalog.

- 

**[hasSubCategories](#hassubcategories)**

Indicates whether the subcategories are available (true) or not (false).

- 

**[id](#id)**

Get the ID of the category.

- 

**[isNavigational](#isnavigational)**

Indicates whether the category node is navigational (true) or not (false).

- 

**[name](#name)**

Get the name of the category. If data translation is set up and specified in the org, the translated name is available.

- 

**[parentCategoryId](#parentcategoryid)**

Get the ID of the parent category.

- 

**[qualificationContext](#qualificationcontext)**

Get the context details of a user, which are used for qualification rules.

- 

**[sortOrder](#sortorder)**

Get the display order of the product category relative to the siblings with the same parent category.

- 

**[childCategories](#childcategories)**

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

Get the name of the category. If data translation is set up and specified in the org, the translated name is available.

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

Type: [runtime_industries_cpq.QualificationContextOutputRepresentation](./apex-class-runtime-industries-cpq-qualificationcontextoutputrepresentation.md#qualificationcontextoutputrepresentation-class)

### sortOrder

Get the display order of the product category relative to the siblings with the same parent category.

#### Signature

`public Integer sortOrder {get; set;}`

#### Property Value

Type: Integer

### childCategories

Get the list of childcategorie.

#### Signature

`public List<runtime_industries_cpq.CategoryOutputRepresentation> childCategories {get; set;}`

#### Property Value

Type: List<[runtime_industries_cpq.CategoryOutputRepresentation](#categoryoutputrepresentation-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-categoryoutputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
