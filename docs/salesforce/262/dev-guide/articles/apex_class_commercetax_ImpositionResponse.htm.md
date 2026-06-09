---
page_id: apex_class_commercetax_ImpositionResponse.htm
title: ImpositionResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_ImpositionResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# ImpositionResponse Class

Stores details of tax impositions from the external tax
engine.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Example

In this
mock
adapter example, the adapter sets the `TaxDetailsResponse.setImposition()` method parameter to null if the request's
document code indicates that the tax calculation didn't require any exceptions. Otherwise,
it creates an instance of `ImpositionResponse` and sets its
SubType and Type values, and then assigns it to `TaxDetailsResponse`.

if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
taxDetailsResponse.setImposition(null);
}else{
commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
imposition.setSubType('subtype');
imposition.setType('type');
taxDetailsResponse.setImposition(imposition);
}

- **[ImpositionResponse Methods](./apex_class_commercetax_ImpositionResponse.htm.md#apex_commercetax_ImpositionResponse_methods)**  
  Learn more about the available methods with the `ImpositionResponse` class.

## ImpositionResponse Methods

Learn more about the available methods with the `ImpositionResponse` class.

The `ImpositionResponse` class includes these
methods.

- **[setId(id)](./apex_class_commercetax_ImpositionResponse.htm.md#apex_commercetax_ImpositionResponse_setId)**  
  Sets the ID field of the `ImpositionResponse` class.
- **[setName(name)](./apex_class_commercetax_ImpositionResponse.htm.md#apex_commercetax_ImpositionResponse_setName)**  
  Sets the Name field of the `ImpositionResponse` class.
- **[setSubType(subType)](./apex_class_commercetax_ImpositionResponse.htm.md#apex_commercetax_ImpositionResponse_setSubType)**  
  Sets the SubType field of the `ImpositionResponse` class.
- **[setType(type)](./apex_class_commercetax_ImpositionResponse.htm.md#apex_commercetax_ImpositionResponse_setType)**  
  Sets the Type field of the `ImpositionResponse` class.

### setId(id)

Sets the ID field of the `ImpositionResponse` class.

#### Signature

`global void
setId(String
id)`

#### Parameters

id
:   Type: String
:   User-defined ID value used for referencing the tax imposition.

#### Return Value

Type: void

### setName(name)

Sets the Name field of the `ImpositionResponse` class.

#### Signature

`global void
setName(String
name)`

#### Parameters

name
:   Type: String
:   Optional user-defined name for the tax imposition response.

#### Return Value

Type: void

### setSubType(subType)

Sets the SubType field of the `ImpositionResponse` class.

#### Signature

`global void
setSubType(String
subType)`

#### Parameters

subType
:   Type: String
:   Many tax calculation organizations use types and subtypes to categorize their tax
    imposition procedures. If the tax engine you use follows this process, set the subtype
    with this parameter.

#### Return Value

Type: void

### setType(type)

Sets the Type field of the `ImpositionResponse` class.

#### Signature

`public void
setType(String
type)`

#### Parameters

type
:   Type: String
:   Many tax calculation organizations use types and subtypes to categorize their tax
    imposition procedures. If the tax engine you use follows this process, set the type with
    this parameter.

#### Return Value

Type: void
