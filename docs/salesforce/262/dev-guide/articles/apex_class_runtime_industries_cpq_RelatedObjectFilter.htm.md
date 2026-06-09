---
page_id: apex_class_runtime_industries_cpq_RelatedObjectFilter.htm
title: RelatedObjectFilter Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_RelatedObjectFilter.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# RelatedObjectFilter Class

Represents a filter for related objects used in product search and discovery, allowing you to filter products based on related object criteria.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[RelatedObjectFilter Properties](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_properties)**  
  Learn more about the properties available with the RelatedObjectFilter class.

## RelatedObjectFilter Properties

Learn more about the properties available with the RelatedObjectFilter
class.

The `RelatedObjectFilter` class includes these
properties.

- **[criteria](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_criteria)**  
  Get or set the list of filter criteria to apply to the related object.
- **[objectName](./apex_class_runtime_industries_cpq_RelatedObjectFilter.htm.md#apex_runtime_industries_cpq_RelatedObjectFilter_objectName)**  
  Get or set the name of the related object to filter by, such as "Account" or "Opportunity".

### criteria

Get or set the list of filter criteria to apply to the related object.

#### Signature

`public List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteria {get; set;}`

#### Property Value

Type: List<runtime\_industries\_cpq.FilterCriteriaInputRepresentation>

### objectName

Get or set the name of the related object to filter by, such as "Account" or "Opportunity".

#### Signature

`public String objectName {get; set;}`

#### Property Value

Type: String
