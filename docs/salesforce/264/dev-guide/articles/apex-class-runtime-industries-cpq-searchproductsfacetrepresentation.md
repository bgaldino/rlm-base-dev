---
page_id: apex-class-runtime-industries-cpq-searchproductsfacetrepresentation
title: SearchProductsFacetRepresentation Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-searchproductsfacetrepresentation.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: apex-namespace-runtime-industries-cpq
legacy_page_id: apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm
fetched_at: 2026-11-25
---

# SearchProductsFacetRepresentation Class

Represents a search facet that provides filtering and categorization options for product search results, such as categories, attributes, or other product characteristics.

## Namespace

[runtime_industries_cpq](./apex-namespace-runtime-industries-cpq.md)

- 

**[SearchProductsFacetRepresentation Properties](#searchproductsfacetrepresentation-properties)**

Learn more about the properties available with the SearchProductsFacetRepresentation class.

## SearchProductsFacetRepresentation Properties

Learn more about the properties available with the SearchProductsFacetRepresentation class.

The `SearchProductsFacetRepresentation` class includes these properties.

- 

**[attributeType](#attributetype)**

Get or set the type of attribute this facet represents, such as “Picklist” or “Text”.

- 

**[displayName](#displayname)**

Get or set the display name of the search facet.

- 

**[displayRank](#displayrank)**

Get or set the display rank that determines the order in which this facet appears in search results.

- 

**[nameOrId](#nameorid)**

Get or set the name or identifier of the attribute or category that this facet represents.

- 

**[values](#values)**

Get or set the list of facet values available for filtering, each representing a distinct option within this facet.

### attributeType

Get or set the type of attribute this facet represents, such as “Picklist” or “Text”.

#### Signature

`public String attributeType {get; set;}`

#### Property Value

Type: String

### displayName

Get or set the display name of the search facet.

#### Signature

`public String displayName {get; set;}`

#### Property Value

Type: String

### displayRank

Get or set the display rank that determines the order in which this facet appears in search results.

#### Signature

`public Integer displayRank {get; set;}`

#### Property Value

Type: Integer

### nameOrId

Get or set the name or identifier of the attribute or category that this facet represents.

#### Signature

`public String nameOrId {get; set;}`

#### Property Value

Type: String

### values

Get or set the list of facet values available for filtering, each representing a distinct option within this facet.

#### Signature

`public List<runtime_industries_cpq.FacetValueRepresentation> values {get; set;}`

#### Property Value

Type: List<runtime_industries_cpq.FacetValueRepresentation>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-runtime-industries-cpq-searchproductsfacetrepresentation.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
