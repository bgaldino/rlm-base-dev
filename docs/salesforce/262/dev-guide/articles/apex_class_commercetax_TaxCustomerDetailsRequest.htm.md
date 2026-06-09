---
page_id: apex_class_commercetax_TaxCustomerDetailsRequest.htm
title: TaxCustomerDetailsRequest Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_TaxCustomerDetailsRequest.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# TaxCustomerDetailsRequest Class

Contains customer details used in tax calculation.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

- **[TaxCustomerDetailsRequest Constructors](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_constructors)**  
  Learn more about the available constructors with the `TaxCustomerDetailsRequest` class.
- **[TaxCustomerDetailsRequest Properties](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_properties)**  
  Learn more about the available properties with the `TaxCustomerDetailsRequest` class.
- **[TaxCustomerDetailsRequest Methods](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_methods)**  
  Learn more about the available methods with the `TaxCustomerDetailsRequest` class.

## TaxCustomerDetailsRequest Constructors

Learn more about the available constructors with the `TaxCustomerDetailsRequest` class.

The `TaxCustomerDetailsRequest` class includes these
constructors.

- **[TaxCustomerDetailsRequest(accountId, code, exemptionNo, exemptionReason)](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_ctor)**  
  Initializes the `TaxCustomerDetailsRequest` object. This constructor is intended for test usage and throws an exception if used outside of the Apex test context.

### TaxCustomerDetailsRequest(accountId, code, exemptionNo, exemptionReason)

Initializes the `TaxCustomerDetailsRequest` object. This constructor is intended for test usage and
throws an exception if used outside of the Apex test context.

#### Signature

`global
TaxCustomerDetailsRequest(String accountId, String code, String exemptionNo, String
exemptionReason)`

#### Parameters

accountId
:   Type: String
:   The customer account
    ID
    for the line items sent for tax calculation.

code
:   Type: String
:   The
    tax
    code used during tax calculation.

exemptionNo
:   Type: String
:   The
    exemption
    number applied to any tax exempt line items.

exemptionReason
:   Type: String
:   The reason that certain line items are tax exempt.

## TaxCustomerDetailsRequest Properties

Learn more about the available properties with the `TaxCustomerDetailsRequest` class.

The `TaxCustomerDetailsRequest` class includes these
properties.

- **[accountId](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_accountId)**  
  Customer account that contains the line items sent for tax calculation.
- **[code](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_code)**  
  Tax code used during tax calculation.
- **[exemptionNo](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_exemptionNo)**  
  Number used to qualify a line item for tax exemption.
- **[exemptionReason](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_exemptionReason)**  
  Reason why a line item qualifies for tax exemption.
- **[taxCertificateId](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_taxCertificateId)**  
  ID of a tax certificate used for tax calculation.

### accountId

Customer account that contains the line items sent for tax
calculation.

#### Signature

`global String
accountId {get;
set;}`

#### Property Value

Type: String

### code

Tax
code used during tax calculation.

#### Signature

`global String code
{get;
set;}`

#### Property Value

Type: String

### exemptionNo

Number used to qualify a line item for tax
exemption.

#### Signature

`global String
exemptionNo {get;
set;}`

#### Property Value

Type: String

### exemptionReason

Reason why a line item qualifies for tax exemption.

#### Signature

`global String
exemptionReason {get;
set;}`

#### Property Value

Type: String

### taxCertificateId

ID of a tax certificate used for tax calculation.

#### Signature

`global String
taxCertificateId {get;
set;}`

#### Property Value

Type: String

## TaxCustomerDetailsRequest Methods

Learn more about the available methods with the `TaxCustomerDetailsRequest` class.

The `TaxCustomerDetailsRequest` class includes these
methods.

- **[equals(obj)](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_equals)**  
  Maintains the integrity of lists of type `TaxCustomerDetailsRequest` by determining the equality of external objects in a list. This method is dynamic and based on the `equals()` method in Java.
- **[hashCode()](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_hashCode)**  
  Maintains the integrity of lists of type `TaxCustomerDetailsRequest` by determining the uniqueness of the external objects in a list.
- **[toString()](./apex_class_commercetax_TaxCustomerDetailsRequest.htm.md#apex_commercetax_TaxCustomerDetailsRequest_toString)**  
  Converts a value to a string.

### equals(obj)

Maintains the integrity of lists of type `TaxCustomerDetailsRequest` by determining the equality of external objects in a
list. This method is dynamic and based on the `equals()`
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

Maintains the integrity of lists of type `TaxCustomerDetailsRequest` by determining the uniqueness of the external objects in
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
