---
page_id: apex_class_commercetax_LineTaxAddressesRequest.htm
title: LineTaxAddressesRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_LineTaxAddressesRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# LineTaxAddressesRequest Class

Stores details of the addresses applied per line item in a tax
calculation request.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[LineTaxAddressesRequest Constructors](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_constructors)**  
  Learn more about the constructors available with the `LineTaxAddressesRequest` class.
- **[LineTaxAddressesRequest Properties](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_properties)**  
  Learn more about the available properties with the `LineTaxAddressesRequest` class.
- **[LineTaxAddressesRequest Methods](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_methods)**  
  Learn more about the available methods with the `LineTaxAddressesRequest` class.

## LineTaxAddressesRequest Constructors

Learn more about the constructors available with the `LineTaxAddressesRequest` class.

The `LineTaxAddressesRequest` class includes these
constructors.

- **[LineTaxAddressesRequest(shipFrom, shipTo, soldTo, billTo, taxEngineAddress)](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_ctor)**  
  Constructor for initializing the required addresses for a line item of the tax addresses request such as the ship to, ship from, and bill to addresses. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.

### LineTaxAddressesRequest(shipFrom, shipTo, soldTo, billTo, taxEngineAddress)

Constructor for initializing the required addresses for a line
item of the tax addresses request such as the ship to, ship from, and bill to
addresses.
This constructor is intended for test usage and throws an exception if used outside of
the Apex test context.

#### Signature

`global LineTaxAddressesRequest(commercetax.TaxAddressRequest
shipFrom, commercetax.TaxAddressRequest shipTo, commercetax.TaxAddressRequest
soldTo, commercetax.TaxAddressRequest billTo, commercetax.TaxAddressRequest
taxEngineAddress)`

#### Parameters

shipFrom
:   [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")
:   Address where a line item was shipped from.

shipTo
:   [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")
:   Address where a line item is shipped to.

soldTo
:   [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")
:   Address of the line item's buyer.

billTo
:   [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")
:   Person or group who was billed for the line item.

taxEngineAddress
:   [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")
:   Address that the tax engine uses to calculate tax.

## LineTaxAddressesRequest Properties

Learn more about the available properties with the `LineTaxAddressesRequest` class.

The `LineTaxAddressesRequest` class includes these
properties.

- **[billTo](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_billTo)**  
  The Bill To address for a line item.
- **[shipFrom](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_shipFrom)**  
  The Ship From address for a line item.
- **[shipTo](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_shipTo)**  
  The Ship To address for a line item.
- **[soldTo](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_soldTo)**  
  The Sold To address for a line item.

### billTo

The Bill To address for a line item.

#### Signature

`global commercetax.TaxAddressRequest billTo {get;
set;}`

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressesRequest.htm.md#apex_class_commercetax_TaxAddressesRequest "Contains methods to get and set tax address values.")

### shipFrom

The Ship From address for a line item.

#### Signature

`global commercetax.TaxAddressRequest shipFrom {get;
set;}`

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest "Contains address details used for tax calculation.")

### shipTo

The Ship To address for a line item.

#### Signature

`global commercetax.TaxAddressRequest shipTo {get;
set;}`

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest "Contains address details used for tax calculation.")

### soldTo

The Sold To address for a line item.

#### Signature

`global commercetax.TaxAddressRequest soldTo {get;
set;}`

#### Property Value

Type: [TaxAddressRequest](./apex_class_commercetax_TaxAddressRequest.htm.md#apex_class_commercetax_TaxAddressRequest "Contains address details used for tax calculation.")

## LineTaxAddressesRequest Methods

Learn more about the available methods with the `LineTaxAddressesRequest` class.

The `LineTaxAddressesRequest` class includes these
methods.

- **[equals(obj)](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_equals)**  
  Maintains the integrity of lists of type `LineTaxAddressesRequest` by determining the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_hashCode)**  
  Maintains the integrity of lists of type `LineTaxAddressesRequest` by determining the uniquness of the external object records in a list.
- **[toString()](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_commercetax_LineTaxAddressesRequest_toString)**  
  Converts a value to a string.

### equals(obj)

Maintains the integrity of lists of type `LineTaxAddressesRequest` by determining the equality of external objects in a list.
This method is dynamic and is based on the `equals()`
method in Java.

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

Maintains the integrity of lists of type `LineTaxAddressesRequest` by determining the uniquness of the external object
records in a list.

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
