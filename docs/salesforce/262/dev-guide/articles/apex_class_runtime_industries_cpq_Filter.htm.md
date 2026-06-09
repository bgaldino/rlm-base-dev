---
page_id: apex_class_runtime_industries_cpq_Filter.htm
title: Filter Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_Filter.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# Filter Class

Contains the criteria property to store the details of a filter criteria, which is used
to filter records.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[Filter Properties](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_runtime_industries_cpq_Filter_properties)**  
  Learn more about the properties available with the Filter class.

## Filter Properties

Learn more about the properties available with the Filter class.

The `Filter` class includes these properties.

- **[criteria](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_runtime_industries_cpq_Filter_criteria)**  
  Get the filter criteria to filter the records.

### criteria

Get the filter criteria to filter the records.

#### Signature

`public List<runtime_industries_cpq.FilterCriteriaInputRepresentation> criteria {get; set;}`

#### Property Value

Type: List<[runtime\_industries\_cpq.FilterCriteriaInputRepresentation](./apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation.htm.md#apex_class_runtime_industries_cpq_FilterCriteriaInputRepresentation "Contains properties to store criteria details to filter records based on supported properties.")>
