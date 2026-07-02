---
page_id: apex_class_commercetax_TaxLineItemRequest.htm
title: TaxLineItemRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxLineItemRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxLineItemRequest Class

Contains line item details of a tax request.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[TaxLineItemRequest Constructors](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_constructors)**  
  Learn more about the constructors available with the `TaxLineItemRequest` class.
- **[TaxLineItemRequest Properties](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_properties)**  
  Learn more about the available properties with the `TaxLineItemRequest` class.
- **[TaxLineItemRequest Methods](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_methods)**  
  Learn more about the available methods with the `TaxLineItemRequest` class.

## TaxLineItemRequest Constructors

Learn more about the constructors available with the `TaxLineItemRequest` class.

The `TaxLineItemRequest` class includes these
constructors.

- **[TaxLineItemRequest(addresses, amount, description, productCode, quantity, lineNumber, taxCode, effectiveDate)](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_ctor)**  
  Initializes the request for the tax line item. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.

### TaxLineItemRequest(addresses, amount, description, productCode, quantity, lineNumber, taxCode, effectiveDate)

Initializes the request for the tax line item. This constructor is
intended for test usage and throws an exception if used outside of the Apex test
context.

#### Signature

`global TaxLineItemRequest(commercetax.LineTaxAddressesRequest
addresses, Double amount, String description, String productCode, Double quantity, String
lineNumber, String taxCode, Datetime effectiveDate)`

```
commercetax.TaxLineItemRequest, newinstance, [commercetax.LineTaxAddressesRequest, Double, String, String, Double, String, String, Datetime], commercetax.TaxLineItemRequest
```

#### Parameters

addresses
:   Type: [LineTaxAddressesRequest](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_class_commercetax_LineTaxAddressesRequest "Stores details of the addresses applied per line item in a tax calculation request.")
:   Information about the addresses applied to each line item in a tax calculation
    request.

amount
:   Type: Double
:   Total amount (in a given currency) represented by a line item sent for tax
    calculation.

description
:   Type: String
:   User-defined description for a tax line item.

productCode
:   Type: String
:   Catalog code for the product represented by the tax line item.

quantity
:   Type: Double
:   Number of units of a given product that the tax line item represents.

lineNumber
:   Type: String
:   Unique number used to identify a tax line item.

taxCode
:   Type: String
:   Code used to identify how tax is calculated for a tax line item.

effectiveDate
:   Type: Datetime
:   This is a user-defined date used for reporting only. For negative invoice lines, this
    parameter represents the invoice date from the original invoice. In other cases, it
    represents the date when the tax transaction takes effect on the line item. The previous
    tax transaction type is always `Debit` for negative
    invoice lines.

## TaxLineItemRequest Properties

Learn more about the available properties with the `TaxLineItemRequest` class.

The `TaxLineItemRequest` class includes these
properties.

- **[addresses](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_addresses)**  
  Contains the list of addresses of a line item.
- **[amount](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_amount)**  
  Total amount (in a given currency) represented by a line item sent for tax calculation.
- **[customTaxAttributes](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_customTaxAttributes)**  
  Customised tax contract to include additional attributes at the line item level.
- **[description](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_description)**  
  User-defined description for a tax line item.
- **[effectiveDate](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_effectiveDate)**  
  The date that a tax transaction takes effect on a line item. This is a user-defined date used for reporting only.
- **[lineNumber](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_lineNumber)**  
  Unique number used to identify a tax line item.
- **[productCode](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_productCode)**  
  Catalog code for the product represented by the tax line item.
- **[productSKU](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_productSKU)**  
  Unique identifier of a product that can be used to identify products that are exempted from tax.
- **[quantity](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_quantity)**  
  Number of units of a given product that the tax line item represents.
- **[referenceDocumentCode](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_referenceDocumentCode)**  
  Identifier that combines the original invoice ID, previous tax transaction type, and tax engine ID, used in tax calculations for negative invoice lines.
- **[taxCode](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_taxCode)**  
  Code used to identify how tax is calculated for a tax line item.

### addresses

Contains the list of addresses of a line item.

#### Signature

`public
commercetax.LineTaxAddressesRequest addresses {get;
set;}`

#### Property Value

Type: [commercetax.LineTaxAddressesRequest](./apex_class_commercetax_LineTaxAddressesRequest.htm.md#apex_class_commercetax_LineTaxAddressesRequest "Stores details of the addresses applied per line item in a tax calculation request.")

### amount

Total amount (in a given currency) represented by a line item sent
for tax calculation.

#### Signature

`global Double amount
{get;
set;}`

#### Property Value

Type: Double

### customTaxAttributes

Customised tax contract to include additional attributes at the line
item level.

#### Signature

`global commercetax.TaxLineItemRequest customTaxAttributes
{get; set;}`

#### Property Value

Type: Map<String, Object>

### description

User-defined description for a tax line item.

#### Signature

`global String
description {get;
set;}`

#### Property Value

Type: String

### effectiveDate

The date that a tax transaction takes effect on a line item. This is
a user-defined date used for reporting only.

#### Signature

`global Datetime
effectiveDate {get;
set;}`

#### Property Value

Type: Datetime

### lineNumber

Unique number used to identify a tax line item.

#### Signature

`global String
lineNumber {get;
set;}`

#### Property Value

Type: String

### productCode

Catalog code for the product represented by the tax line
item.

#### Signature

`global String
productCode {get;
set;}`

#### Property Value

Type: String

### productSKU

Unique identifier of a product that can be used to identify products
that are exempted from tax.

#### Signature

`global String productSKU {get; set;}`

#### Property Value

Type: String

### quantity

Number of units of a given product that the tax line item
represents.

#### Signature

`global Double
quantity {get;
set;}`

#### Property Value

Type: Double

### referenceDocumentCode

Identifier that combines the original invoice ID, previous tax
transaction type, and tax engine ID, used in tax calculations for negative invoice
lines.

For example, a referenceDocumentCode parameter value `3ttxx00000004Bh_Debit-4wAxx0000000001EAA` indicates `3ttxx00000004Bh` is the original invoice ID and `4wAxx0000000001EAA` is the tax engine ID. The previous tax transaction type is
always `Debit` for negative invoice lines.

#### Signature

`global String referenceDocumentCode {get; set;}`

#### Property Value

Type: String

### taxCode

Code used to identify how tax is calculated for a tax line
item.

#### Signature

`global String
taxCode {get;
set;}`

#### Property Value

Type: String

## TaxLineItemRequest Methods

Learn more about the available methods with the `TaxLineItemRequest` class.

The `TaxLineItemRequest` class includes these
methods.

- **[equals(obj)](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_equals)**  
  Maintains the integrity of lists of type `TaxLineItemRequest` by determining the equality of external objects in a list. This method is dynamic and is based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_hashCode)**  
  Maintains the integrity of lists of type `TaxLineItemRequest` by determining the uniqueness of the external object records in a list.
- **[toString()](./apex_class_commercetax_TaxLineItemRequest.htm.md#apex_commercetax_TaxLineItemRequest_toString)**  
  Converts a value to a string.

### equals(obj)

Maintains the integrity of lists of type `TaxLineItemRequest` by determining the equality of external objects in a list. This
method is dynamic and is based on the `equals()` method in
Java.

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

Maintains the integrity of lists of type `TaxLineItemRequest` by determining the uniqueness of the external object records in
a list.

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
