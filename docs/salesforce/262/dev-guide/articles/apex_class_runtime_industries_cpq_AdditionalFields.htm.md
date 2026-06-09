---
page_id: apex_class_runtime_industries_cpq_AdditionalFields.htm
title: AdditionalFields Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_runtime_industries_cpq_AdditionalFields.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: apex_namespace_runtime_industries_cpq.htm
fetched_at: 2026-06-09
---

# AdditionalFields Class

Contains properties to include a map where the key is a string and the value is an
instance of the AdditionalFieldsInput class.

## Namespace

[runtime\_industries\_cpq](./apex_namespace_runtime_industries_cpq.htm.md "The runtime_industries_cpq namespace provides classes and methods to search products or to manage products, catalogs, and categories.")

- **[AdditionalFields Properties](./apex_class_runtime_industries_cpq_AdditionalFields.htm.md#apex_runtime_industries_cpq_AdditionalFields_properties)**  
  Set the AdditionalFields class property to include a map where the key is a string and the value is an instance of the AdditionalFieldsInput class.

## AdditionalFields Properties

Set the AdditionalFields class property to include a map where the key is a string and
the value is an instance of the AdditionalFieldsInput class.

The `AdditionalFields` class includes this property.

- **[additionalFields](./apex_class_runtime_industries_cpq_AdditionalFields.htm.md#apex_runtime_industries_cpq_AdditionalFields_additionalFields)**  
  Includes a map where the key is a string and the value is an instance of the AdditionalFieldsInput class.

### additionalFields

Includes a map where the key is a string and the value is an instance of the
AdditionalFieldsInput class.

#### Signature

`public Map<String,runtime_industries_cpq.AdditionalFieldsInput> additionalFields {get; set;}`

#### Property Value

Type: Map<String,[runtime\_industries\_cpq.AdditionalFieldsInput](./apex_class_runtime_industries_cpq_AdditionalFieldsInput.htm.md#apex_class_runtime_industries_cpq_AdditionalFieldsInput "Contains properties to include the additional standard or custom fields in the request.")>
