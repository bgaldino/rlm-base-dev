---
page_id: apex-class-runtime-industries-cpq-filterinputrepresentation
title: FilterInputRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-filterinputrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_FilterInputRepresentation.htm
fetched_at: 2026-11-25
---

# FilterInputRepresentation Class

Contains the filter property to filters records based on supported criteria.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[FilterInputRepresentation Properties](#filterinputrepresentation-properties)**

Learn more about the available properties with the FilterInputRepresentation class.

## FilterInputRepresentation Properties

Learn more about the available properties with the FilterInputRepresentation class.

The `FilterInputRepresentation` class includes these properties.

- 

**[filter](#filter)**

Filters records based on supported criteria. The supported property is name.

### filter

Filters records based on supported criteria. The supported property is name.

#### Signature

`public runtime_industries_cpq.Filter filter {get; set;}`

#### Property Value

Type: [runtime_industries_cpq.Filter](./apex-class-runtime-industries-cpq-filter.md#filter-class)

#### Usage

The supported operators are:

- `eq`

- `in`

- `contains`—This value isn’t applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled.

If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-filterinputrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
