---
page_id: apex-class-runtime-industries-cpq-filtercriteriainputrepresentation
title: FilterCriteriaInputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-filtercriteriainputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm
fetched_at: 2026-11-25
---

# FilterCriteriaInputRepresentation Class

Contains properties to store criteria details to filter records based on supported properties.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[FilterCriteriaInputRepresentation Properties](#filtercriteriainputrepresentation-properties)**

Learn more about the properties available with the FilterCriteriaInputRepresentation class.

## FilterCriteriaInputRepresentation Properties

Learn more about the properties available with the FilterCriteriaInputRepresentation class.

The `FilterCriteriaInputRepresentation` class includes these properties.

- 

**[attributeType](#attributetype)**

Get details of the search attribute type of the facet for a faceted search.

- 

**[operator](#operator)**

Get the operator that’s used for the filter criteria.

- 

**[property](#property)**

Get the property name to use in the filter, which must be the same as the object field. The supported property is name.

- 

**[value](#value)**

Get the value for the filter criteria.

### attributeType

Get details of the search attribute type of the facet for a faceted search.

#### Signature

`public String attributeType {get; set;}`

#### Property Value

Type: String

#### Usage

Valid values are:

- `ProductStandard`

- `ProductCustom`

- `ProductDynamicAttribute`

- `ProductAttributeStandard`

- `ProductAttributeCustom`

### operator

Get the operator that’s used for the filter criteria.

#### Signature

`public String operator {get; set;}`

#### Property Value

Type: String

#### Usage

The supported operators are:

- `eq`

- `in`

- `contains`

- `gt`—Specifies a greater than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `lt`—Specifies a less than criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `gte`—Specifies a greater than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

- `lte`—Specifies a less than or equal to criteria. Available from API version 63.0 and later for Number, Date, and Datetime data types only.

### property

Get the property name to use in the filter, which must be the same as the object field. The supported property is name.

#### Signature

`public String property {get; set;}`

#### Property Value

Type: String

### value

Get the value for the filter criteria.

#### Signature

`public String value {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-filtercriteriainputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
