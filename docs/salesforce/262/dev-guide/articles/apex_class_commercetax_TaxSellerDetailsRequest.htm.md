---
page_id: apex_class_commercetax_TaxSellerDetailsRequest.htm
title: TaxSellerDetailsRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxSellerDetailsRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxSellerDetailsRequest Class

Contains tax code details used in the tax calculation
request.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[TaxSellerDetailsRequest Constructors](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_constructors)**  
  Learn more about the available constructors with the `TaxSellerDetailsRequest` class.
- **[TaxSellerDetailsRequest Properties](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_properties)**  
  Learn more about the available properties with the `TaxSellerDetailsRequest` class.
- **[TaxSellerDetailsRequest Methods](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_methods)**  
  Learn more about the available methods with the `TaxSellerDetailsRequest` class.

## TaxSellerDetailsRequest Constructors

Learn more about the available constructors with the `TaxSellerDetailsRequest` class.

The `TaxSellerDetailsRequest` class includes these
constructors.

- **[TaxSellerDetailsRequest(code)](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_ctor)**  
  Initializes the request for the tax seller details. This constructor is intended for test usage and throws an exception if used outside of the Apex test context

### TaxSellerDetailsRequest(code)

Initializes the request for the tax seller details. This constructor
is intended for test usage and throws an exception if used outside of the Apex test
context

#### Signature

`global
TaxSellerDetailsRequest(String
code)`

#### Parameters

code
:   Type: String
:   Tax code used for tax calculation.

## TaxSellerDetailsRequest Properties

Learn more about the available properties with the `TaxSellerDetailsRequest` class.

The `TaxSellerDetailsRequest` class includes these
properties.

- **[code](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_code)**  
  Tax code used for tax calculation.

### code

Tax code used for tax calculation.

#### Signature

`global String code
{get;
set;}`

#### Property Value

Type: String

## TaxSellerDetailsRequest Methods

Learn more about the available methods with the `TaxSellerDetailsRequest` class.

The `TaxSellerDetailsRequest` class includes these
methods.

- **[equals(obj)](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_equals)**  
  Maintains the integrity of lists of type `TaxSellerDetailsRequest` by determining the equality of the external objects in a list. This method is dynamic and based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_hashCode)**  
  Maintains the integrity of lists of type `TaxSellerDetailsRequest` by determining the uniqueness of the external objects in a list.
- **[toString()](./apex_class_commercetax_TaxSellerDetailsRequest.htm.md#apex_commercetax_TaxSellerDetailsRequest_toString)**  
  Converts a value to a string.

### equals(obj)

Maintains the integrity of lists of type `TaxSellerDetailsRequest` by determining the equality of the external objects in a
list. This method is dynamic and based on the `equals()`
method in Java.

#### Signature

`global Boolean
equals(Object
obj)`

#### Parameters

obj
:   Type: Object
:   External object whose key is to be validated.

#### Return Value

Type: Boolean

### hashCode()

Maintains the integrity of lists of type `TaxSellerDetailsRequest` by determining the uniqueness of the external objects in a
list.

#### Signature

`global Integer
hashCode()`

#### Return Value

Type: Integer

### toString()

Converts a value to a string.

#### Signature

`global String
toString()`

#### Return Value

Type: String
