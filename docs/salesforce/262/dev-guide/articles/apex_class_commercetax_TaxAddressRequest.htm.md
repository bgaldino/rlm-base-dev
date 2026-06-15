---
page_id: apex_class_commercetax_TaxAddressRequest.htm
title: TaxAddressRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxAddressRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxAddressRequest Class

Contains address details used for tax calculation.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[TaxAddressRequest Constructors](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_constructors)**  
  Learn more about the available constructors with the `TaxAddressRequest` class.
- **[TaxAddressRequest Properties](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_properties)**  
  Learn more about the available properties with the `TaxAddressRequest` class.
- **[TaxAddressRequest Methods](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_methods)**  
  Learn more about the available methods with the `TaxAddressRequest` class.

## TaxAddressRequest Constructors

Learn more about the available constructors with the `TaxAddressRequest` class.

The `TaxAddressRequest` class includes these
constructors.

- **[TaxAddressRequest(city, country, latitude, longitude, postalCode, state, street, locationCode)](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_ctor)**  
  Initializes the `TaxAddressRequest` object using address details. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.

### TaxAddressRequest(city, country, latitude, longitude, postalCode, state, street, locationCode)

Initializes the `TaxAddressRequest`
object using address details. This constructor is intended for test usage and throws an
exception if used outside of the Apex test context.

#### Signature

`global TaxAddressRequest(String city, String country, Double
latitude, Double longitude, String postalCode, String state, String street, String
locationCode)`

#### Parameters

city
:   Type: String
:   City used in an address, which is required for tax calculation.

country
:   Type: String
:   Country used in an address, which is required for tax calculation.

latitude
:   Type: Double
:   Latitude used in an address, which is required for tax calculation.

longitude
:   Type: Double
:   Longitude used in an address, which is required for tax calculation.

postalCode
:   Type: String
:   Postal code used in an address, which is required for tax calculation.

state
:   Type: String
:   State used in an address, which is required for tax calculation.

street
:   Type: String
:   Street used in an address, which is required for tax calculation.

locationCode
:   Type: String
:   Location code used in an address, which is required for tax calculation.

## TaxAddressRequest Properties

Learn more about the available properties with the `TaxAddressRequest` class.

The `TaxAddressRequest` class includes these
properties.

- **[city](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_city)**  
  City used in an address, which is required for tax calculation.
- **[country](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_country)**  
  Country used in an address, which is required for tax calculation.
- **[countryCode](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_countryCode)**  
  Country code used in an address, which is required for tax calculation.
- **[latitude](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_latitude)**  
  Latitude used in an address, which is required for tax calculation.
- **[locationCode](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_locationCode)**  
  Location code used in an address, which is required for tax calculation.
- **[longitude](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_longitude)**  
  Longitude used in an address, which is required for tax calculation.
- **[postalCode](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_postalCode)**  
  Postal code used in an address, which is required for tax calculation.
- **[state](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_state)**  
  State used in an address, which is required for tax calculation.
- **[stateCode](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_stateCode)**  
  State code used in an address, which is required for tax calculation.
- **[street](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_street)**  
  Street used in an address, which is required for tax calculation.

### city

City used in an address, which is required for tax
calculation.

#### Signature

`global String city
{get;
set;}`

#### Property Value

Type: String

### country

Country used in an address, which is required for tax
calculation.

#### Signature

`global String
country {get;
set;}`

#### Property Value

Type: String

### countryCode

Country code used in an address, which is required for tax
calculation.

#### Signature

`global String countryCode {get; set;}`

#### Property Value

Type: String

### latitude

Latitude used in an address, which is required for tax
calculation.

#### Signature

`global Double
latitude {get;
set;}`

#### Property Value

Type: Double

### locationCode

Location code used in an address, which is required for tax
calculation.

#### Signature

`global String
locationCode {get;
set;}`

#### Property Value

Type: String

### longitude

Longitude used in an address, which is required for tax
calculation.

#### Signature

`global Double
longitude {get;
set;}`

#### Property Value

Type: Double

### postalCode

Postal code used in an address, which is required for tax
calculation.

#### Signature

`global String
postalCode {get;
set;}`

#### Property Value

Type: String

### state

State used in an address, which is required for tax
calculation.

#### Signature

`global String state
{get;
set;}`

#### Property Value

Type: String

### stateCode

State code used in an address, which is required for tax
calculation.

#### Signature

`global String stateCode {get; set;}`

#### Property Value

Type: String

### street

Street used in an address, which is required for tax
calculation.

#### Signature

`global String street
{get;
set;}`

#### Property Value

Type: String

## TaxAddressRequest Methods

Learn more about the available methods with the `TaxAddressRequest` class.

The `TaxAddressRequest` class includes these
methods.

- **[equals(obj)](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_equals)**  
  Maintains the integrity of lists of type TaxAddressRequest by determining the equality of external objects in a list. This method is dynamic and based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_hashCode)**  
  Maintains the integrity of lists of type `TaxAddressRequest` by determining the uniqueness of the external object in a list.
- **[toString()](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_commercetax_TaxAddressRequest_toString)**  
  Converts a date to a string.

### equals(obj)

Maintains the integrity of lists of type TaxAddressRequest by
determining the equality of external objects in a list. This method is dynamic and based on
the `equals()` method in Java.

#### Signature

`global Boolean
equals(Object
obj)`

#### Parameters

obj
:   Type: Object
:   External object whose
    key
    is to be validated.

#### Return Value

Type: Boolean

### hashCode()

Maintains the integrity of lists of type `TaxAddressRequest` by determining the uniqueness of the external object in a
list.

#### Signature

`global Integer
hashCode()`

#### Return Value

Type: Integer

### toString()

Converts a date to a string.

#### Signature

`global String
toString()`

#### Return Value

Type: String
