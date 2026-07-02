---
page_id: apex_class_commercetax_CustomTaxAttributesResponse.htm
title: CustomTaxAttributesResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CustomTaxAttributesResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# CustomTaxAttributesResponse Class

Sets additional data or custom attributes in the tax
response.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[CustomTaxAttributesResponse Constructors](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_constructors)**  
  Learn more about the available constructors with the `CustomTaxAttributesResponse` class.
- **[CustomTaxAttributesResponse Methods](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_methods)**  
  Learn more about the available methods with the `CustomTaxAttributesResponse` class.

## CustomTaxAttributesResponse Constructors

Learn more about the available constructors with the `CustomTaxAttributesResponse` class.

The `CustomTaxAttributesResponse` class includes
these constructors.

- **[CustomTaxAttributesResponse()](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_ctor)**  
  Constructor to set additional data or custom attributes in the tax response.

### CustomTaxAttributesResponse()

Constructor to set additional data or custom attributes in the tax
response.

#### Signature

`global CustomTaxAttributesResponse()`

## CustomTaxAttributesResponse Methods

Learn more about the available methods with the `CustomTaxAttributesResponse` class.

The `CustomTaxAttributesResponse` class includes
these methods.

- **[setData(data)](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_commercetax_CustomTaxAttributesResponse_setData)**  
  Sets additional data or custom attributes in the tax response.

### setData(data)

Sets additional data or custom attributes in the tax
response.

#### Signature

`global void setData(Map<String, Object>
data)`

#### Parameters

data
:   Type: Map<String, Object>
:   Additional data or custom attributes to be included in the tax response.

#### Return Value

Type: void
