---
page_id: apex_class_commercetax_JurisdictionResponse.htm
title: JurisdictionResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_JurisdictionResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# JurisdictionResponse Class

Stores details from the external tax engine about the tax
jurisdiction used in the tax calculation process. A tax jurisdiction represents a government
entity that collects tax.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Example

In
this
mock adapter example, the adapter sets the `TaxDetailsResponse.setJurisdiction()` method parameter to null if the request's
document code indicates that the tax calculation didn't require any exceptions. Otherwise,
it creates an instance of `JurisdictionResponse` and sets
its address values. Because this code represents a mock adapter, the example defines the
address parameters directly. In a standard implementation, the jurisdiction's setters
receive values passed from the eternal tax engine.

if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
taxDetailsResponse.setJurisdiction(null);
}else{
commercetax.JurisdictionResponse jurisdiction = new commercetax.JurisdictionResponse();
jurisdiction.setCountry('country');
jurisdiction.setRegion('region');
jurisdiction.setName('name');
jurisdiction.setStateAssignedNumber('stateAssignedNo');
jurisdiction.setId('id');
jurisdiction.setLevel('level');
taxDetailsResponse.setJurisdiction(jurisdiction);
}

- **[JurisdictionResponse Methods](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_methods)**  
  Learn more about the available methods with the `JurisdictionResponse` class.

## JurisdictionResponse Methods

Learn more about the available methods with the `JurisdictionResponse` class.

The `JurisdictionResponse` class includes these
methods.

- **[setCountry(country)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setCountry)**  
  Sets the Country field of the `JurisdictionResponse` class.
- **[setId(id)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setId)**  
  Sets the ID field of the `JurisdictionResponse` class.
- **[setLevel(level)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setLevel)**  
  Sets the Level field of the `JurisdictionResponse` class.
- **[setName(name)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setName)**  
  Sets the Name field of the `JurisdictionResponse` class.
- **[setRegion(region)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setRegion)**  
  Sets the Region value of the `JurisdictionResponse` class.
- **[setStateAssignedNumber(stateAssignedNo)](./apex_class_commercetax_JurisdictionResponse.htm.md#apex_commercetax_JurisdictionResponse_setStateAssignedNumber)**  
  Sets the StateAssignedNumber field of the `JurisdictionResponse` class.

### setCountry(country)

Sets the Country field of the `JurisdictionResponse` class.

#### Signature

`global void
setCountry(String
country)`

#### Parameters

country
:   Type: String
:   The country of the tax jurisdiction entity's address.

#### Return Value

Type: void

### setId(id)

Sets the ID field of the `JurisdictionResponse` class.

#### Signature

`global void
setId(String
id)`

#### Parameters

id
:   Type: String
:   User-defined Id value used to reference the jurisdiction response.

#### Return Value

Type: void

### setLevel(level)

Sets the Level field of the `JurisdictionResponse` class.

#### Signature

`global void
setLevel(String
level)`

#### Parameters

level
:   Type: String
:   Level
    value used in the jurisdiction entity's address.

#### Return Value

Type: void

### setName(name)

Sets the Name field of the `JurisdictionResponse` class.

#### Signature

`global void
setName(String
name)`

#### Parameters

name
:   Type: String
:   Optional user-defined name field for referencing the jurisdiction response.

#### Return Value

Type: void

### setRegion(region)

Sets the Region value of the `JurisdictionResponse` class.

#### Signature

`global void
setRegion(String
region)`

#### Parameters

region
:   Type: String
:   Region value used in the tax jurisdiction entity's address.

#### Return Value

Type: void

### setStateAssignedNumber(stateAssignedNo)

Sets the StateAssignedNumber field of the `JurisdictionResponse` class.

#### Signature

`global void
setStateAssignedNumber(String
stateAssignedNo)`

#### Parameters

stateAssignedNo
:   Type: String
:   State assigned number value of the tax jurisdiction entity's address.

#### Return Value

Type: void
