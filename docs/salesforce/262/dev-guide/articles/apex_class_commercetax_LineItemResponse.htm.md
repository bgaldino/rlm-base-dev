---
page_id: apex_class_commercetax_LineItemResponse.htm
title: LineItemResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_LineItemResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# LineItemResponse Class

Response class that stores details of a list of one or more line
items on which the tax engine has calculated tax.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Example

This example uses a `LineItemResponse` list to store
information about each line item that was processed as part of the request. For
simplicity, the sample code uses a static value of 1 for the tax rate. However, most
integrations typically have a more complex process for determining a tax rate. Most
integrations also build a `TaxDetailsResponse` list
to store the actual tax value information that they assign to each line item in the
`LineItemResponse` list.

Double totalTax = 0.0;
Double totalAmount = 0.0;
List<commercetax.LineItemResponse> lineItemResponses = new List<commercetax.LineItemResponse>();
for(Commercetax.TaxLineItemRequest lineItem : request.lineItems){
commercetax.AddressesResponse addressesRes = new commercetax.AddressesResponse();
if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
addressesRes.setShipFrom(null);
addressesRes.setShipTO(null);
addressesRes.setSoldTo(null);
}else{
commercetax.AddressResponse addRes = new commercetax.AddressResponse();
addRes.setLocationCode('locationCode');
addressesRes.setShipFrom(addRes);
addressesRes.setShipTO(addRes);
addressesRes.setSoldTo(addRes);
}
commercetax.LineItemResponse lineItemResponse = new commercetax.LineItemResponse();
Double totalLineTax = 0;
List<commercetax.TaxDetailsResponse> taxDetailsResponses = new List<commercetax.TaxDetailsResponse>();
for(integer i =0;i<1;i++){
Integer rate = 1;
Double taxableAmount = lineItem.amount;
commercetax.TaxDetailsResponse taxDetailsResponse = new commercetax.TaxDetailsResponse();
taxDetailsResponse.setRate(Double.valueOf(rate));
taxDetailsResponse.setTaxableAmount(taxableAmount);
Double tax = taxableAmount\*rate;
totalLineTax+=tax;
taxDetailsResponse.setTax(taxableAmount\*rate);
taxDetailsResponse.setExemptAmount(0);
taxDetailsResponse.setExemptReason('exemptReason');
taxDetailsResponse.setTaxRegionId('taxRegionId');
taxDetailsResponse.setTaxId(String.valueOf(getRandomInteger(0,2323233)));
taxDetailsResponse.setSerCode('serCode');
taxDetailsResponse.setTaxAuthorityTypeId('taxAuthorityTypeId');
if(request.DocumentCode == 'SetsNullForResponseWithoutException'){
taxDetailsResponse.setImposition(null);
}else{
commercetax.ImpositionResponse imposition = new commercetax.ImpositionResponse();
imposition.setSubType('subtype');
imposition.setType('type');
taxDetailsResponse.setImposition(imposition);
}
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
taxDetailsResponses.add(taxDetailsResponse);
}
lineItemResponse.setTaxes(taxDetailsResponses);
totalTax +=totalLineTax;
totalAmount+=lineItem.amount;

- **[LineItemResponse Methods](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_methods)**  
  Learn more about the available methods with the `LineItemResponse` class.

## LineItemResponse Methods

Learn more about the available methods with the `LineItemResponse` class.

The `LineItemResponse` class includes these
methods.

- **[setAddresses(addresses)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setAddresses)**  
  Sets the Addresses field on the `LineItemResponse` using an instance of `AddressesResponse` class.
- **[setAmountDetails(amountDetails)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setAmountDetails)**  
  Sets the Amount Details field on the `LineItemResponse` using an instance of `AmountDetails`.
- **[setCustomTaxAttributes(customTaxAttributes)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setCustomTaxAttributes)**  
  Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax response at line item level.
- **[setEffectiveDate(effectiveDate)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setEffectiveDate)**  
  Sets the EffectiveDate field on the `LineItemResponse` class. Effective Date fields are optional fields that store the date that a transaction takes effect. We provide these fields only for recordkeeping purposes – for example, if you must report an effective date to an external general ledger system. Salesforce doesn't use them to calculate any tax or payment values.
- **[setIsTaxable(isTaxable)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setIsTaxable)**  
  Sets the IsTaxable field on the `LineItemResponse` class.
- **[setLineNumber(lineNumber)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setLineNumber)**  
  Sets the LineNumber field on the `LineItemResponse` class.
- **[setProductCode(productCode)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setProductCode)**  
  Sets the ProductCode field on the `LineItemResponse` class.
- **[setQuantity(quantity)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setQuantity)**  
  Sets the Quantity field on the `LineItemResponse` class.
- **[setTaxCode(taxCode)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setTaxCode)**  
  Sets the TaxCode field on the `LineItemResponse`.
- **[setTaxes(taxes)](./apex_class_commercetax_LineItemResponse.htm.md#apex_commercetax_LineItemResponse_setTaxes)**  
  Sets the Taxes field on a `LineItemResponse`.

### setAddresses(addresses)

Sets the Addresses field on the `LineItemResponse` using an instance of `AddressesResponse` class.

#### Signature

`global void setAddresses(commercetax.AddressesResponse
addresses)`

#### Parameters

addresses
:   Type: [AddressesResponse](./apex_class_commercetax_AddressesResponse.htm.md#apex_class_commercetax_AddressesResponse "Sets the tax address fields based on a response from the external tax engine. Contains setter methods for the Ship From, Ship To, and Sold To addresses.")
:   Class that contains methods to set the Ship To, Ship From, and Sold To address
    information.

#### Return Value

Type: void

### setAmountDetails(amountDetails)

Sets the Amount Details field on the `LineItemResponse` using an instance of `AmountDetails`.

#### Signature

`global void setAmountDetails(commercetax.AmountDetailsResponse
amountDetails)`

#### Parameters

amountDetails
:   Type: [AmountDetailsResponse](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_class_commercetax_AmountDetailsResponse "Sets tax amount fields based on a response from the external tax engine.")
:   Class that contains methods to set the tax amount, total amount with tax, total
    amount, and exempt amount.

#### Return Value

Type: void

### setCustomTaxAttributes(customTaxAttributes)

Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax
response at line item level.

#### Signature

`global void
setCustomTaxAttributes(commercetax.CustomTaxAttributesResponse
customTaxAttributes)`

#### Parameters

customTaxAttributes
:   Type: [CustomTaxAttributesResponse](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_class_commercetax_CustomTaxAttributesResponse "Sets additional data or custom attributes in the tax response.")
:   Additional data or custom attributes to include in the tax response.

#### Return Value

Type: void

### setEffectiveDate(effectiveDate)

Sets the EffectiveDate field on the `LineItemResponse` class. Effective Date fields are optional fields that store the
date that a transaction takes effect. We provide these fields only for recordkeeping purposes
– for example, if you must report an effective date to an external general ledger
system. Salesforce doesn't use them to calculate any tax or payment values.

#### Signature

`global void
setEffectiveDate(Datetime
effectiveDate)`

#### Parameters

effectiveDate
:   Type: Datetime
:   Optional field that stores the date that a transaction takes effect.

#### Return Value

Type: void

### setIsTaxable(isTaxable)

Sets the IsTaxable field on the `LineItemResponse` class.

#### Signature

`global void
setIsTaxable(Boolean
isTaxable)`

#### Parameters

isTaxable
:   Type: Boolean
:   Whether line items were taxed as part of the tax calculation request.

#### Return Value

Type: void

### setLineNumber(lineNumber)

Sets the LineNumber field on the `LineItemResponse` class.

#### Signature

`global void
setLineNumber(String
lineNumber)`

#### Parameters

lineNumber
:   Type: String
:   User-defined number used to identify a line item.

#### Return Value

Type: void

### setProductCode(productCode)

Sets the ProductCode field on the `LineItemResponse` class.

#### Signature

`global void
setProductCode(String
productCode)`

#### Parameters

productCode
:   Type: String
:   Code for the product that a line item represents.

#### Return Value

Type: void

### setQuantity(quantity)

Sets the Quantity field on the `LineItemResponse` class.

#### Signature

`global void
setQuantity(Double
quantity)`

#### Parameters

quantity
:   Type: Double
:   Quantity of a line item.

#### Return Value

Type: void

### setTaxCode(taxCode)

Sets the TaxCode field on the `LineItemResponse`.

#### Signature

`global void
setTaxCode(String
taxCode)`

#### Parameters

taxCode
:   Type: String
:   Federal code that an individual or business uses to pay their taxes to a federal or
    state government. The tax engine uses this code during the tax calculation process.

#### Return Value

Type: void

### setTaxes(taxes)

Sets the Taxes field on a `LineItemResponse`.

#### Signature

`global void setTaxes(List<commercetax.TaxDetailsResponse>
taxes)`

#### Parameters

taxes
:   Type: List<[TaxDetailsResponse](./apex_class_commercetax_TaxDetailsResponse.htm.md#apex_class_commercetax_TaxDetailsResponse "Stores details of the tax values that an external tax engine calculates in response to a tax calculation request.")>
:   Tax values applied to a line item in the `LineItemResponse` list. This information is stored in a list of `TaxDetailsResponses`, which contains values such as tax,
    taxable amount, and tax rate.

#### Return Value

Type: void
