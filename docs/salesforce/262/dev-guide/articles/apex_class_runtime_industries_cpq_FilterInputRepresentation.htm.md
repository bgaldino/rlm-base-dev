---
page_id: apex_class_runtime_industries_cpq_FilterInputRepresentation.htm
title: FilterInputRepresentation Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_FilterInputRepresentation.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# FilterInputRepresentation Class

Contains the filter property to filters records based on supported criteria.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[FilterInputRepresentation Properties](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterInputRepresentation_properties)**  
  Learn more about the available properties with the FilterInputRepresentation class.

## FilterInputRepresentation Properties

Learn more about the available properties with the FilterInputRepresentation
class.

The `FilterInputRepresentation` class includes these
properties.

- **[filter](./apex_class_runtime_industries_cpq_FilterInputRepresentation.htm.md#apex_runtime_industries_cpq_FilterInputRepresentation_filter)**  
  Filters records based on supported criteria. The supported property is name.

### filter

Filters records based on supported criteria. The supported property is name.

#### Signature

`public runtime_industries_cpq.Filter filter {get; set;}`

#### Property Value

Type: [runtime\_industries\_cpq.Filter](./apex_class_runtime_industries_cpq_Filter.htm.md#apex_class_runtime_industries_cpq_Filter "Contains the criteria property to store the details of a filter criteria, which is used to filter records.")

#### Usage

The supported operators are:

- `eq`
- `in`
- `contains`—This value isn't
  applicable if the **Use Indexed Data For Product Listing and
  Search** toggle from the Product Discovery Settings page from
  Setup is enabled.

If multiple criteria are specified, then the resultant criteria are combined by using the
`and` operator.
