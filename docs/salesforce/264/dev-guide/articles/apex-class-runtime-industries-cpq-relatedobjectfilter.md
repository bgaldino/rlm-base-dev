---
page_id: apex-class-runtime-industries-cpq-relatedobjectfilter
title: RelatedObjectFilter Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-relatedobjectfilter.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_RelatedObjectFilter.htm
fetched_at: 2026-11-25
---

# RelatedObjectFilter Class

Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[RelatedObjectFilter Properties](#relatedobjectfilter-properties)**

Learn more about the properties available with the RelatedObjectFilter class.

## RelatedObjectFilter Properties

Learn more about the properties available with the RelatedObjectFilter class.

The `RelatedObjectFilter` class includes these properties.

- 

**[criteria](#criteria)**

Get or set the list of filter criteria to apply to the related object.

- 

**[objectName](#objectname)**

Get or set the name of the related object to filter by, such as “Account” or “Opportunity”.

### criteria

Get or set the list of filter criteria to apply to the related object.

#### Signature

`public List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteria {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.FilterCriteriaInputRepresentation>

### objectName

Get or set the name of the related object to filter by, such as “Account” or “Opportunity”.

#### Signature

`public String objectName {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-relatedobjectfilter.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
