---
page_id: apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm
title: SearchProductsFacetRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# SearchProductsFacetRepresentation Class

Represents a search facet that provides filtering and categorization options for product search results, such as categories, attributes, or other product characteristics.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[SearchProductsFacetRepresentation Properties](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_properties)**  
  Learn more about the properties available with the SearchProductsFacetRepresentation class.

## SearchProductsFacetRepresentation Properties

Learn more about the properties available with the SearchProductsFacetRepresentation
class.

The `SearchProductsFacetRepresentation` class includes
these properties.

- **[attributeType](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_attributeType)**  
  Get or set the type of attribute this facet represents, such as "Picklist" or "Text".
- **[displayName](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_displayName)**  
  Get or set the display name of the search facet.
- **[displayRank](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_displayRank)**  
  Get or set the display rank that determines the order in which this facet appears in search results.
- **[nameOrId](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_nameOrId)**  
  Get or set the name or identifier of the attribute or category that this facet represents.
- **[values](./apex_class_runtime_industries_cpq_SearchProductsFacetRepresentation.htm.md#apex_runtime_industries_cpq_SearchProductsFacetRepresentation_values)**  
  Get or set the list of facet values available for filtering, each representing a distinct option within this facet.

### attributeType

Get or set the type of attribute this facet represents, such as "Picklist" or "Text".

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

Type: List<runtime\_industries\_cpq.FacetValueRepresentation>
