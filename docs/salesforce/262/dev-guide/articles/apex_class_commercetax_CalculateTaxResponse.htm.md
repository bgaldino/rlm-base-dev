---
page_id: apex_class_commercetax_CalculateTaxResponse.htm
title: CalculateTaxResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_CalculateTaxResponse.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-06-09
---

# CalculateTaxResponse Class

Sets
the values of the tax transaction following a response from the external tax engine.
Extends the [AbstractTransactionResponse](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_class_commercetax_AbstractTransactionResponse "Abstract class that contains methods for setting tax fields based on the external tax provider's response. Response classes that extend AbstractTransactionResponse inherit these methods.") class and is the top-level response
class.

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md "Manage the communication between Salesforce and an external tax engine.")

## Example

```
if(requestType == commercetax.RequestType.CalculateTax){
             commercetax.calculatetaxtype type = request.taxtype;
             String docCode='';
             if(request.DocumentCode == 'simulateEmptyDocumentCode')
                 docCode = '';
             else if(request.DocumentCode != null)
                 docCode =request.DocumentCode;
             else if(request.ReferenceEntityId != null) docCode = request.ReferenceEntityId;
             else docCode =  String.valueOf(getRandomInteger(0,2147483647));
             commercetax.CalculateTaxResponse response = new commercetax.CalculateTaxResponse();
             if(request.isCommit == true) {
                 response.setStatus(commercetax.TaxTransactionStatus.Committed);
             } else {
                 response.setStatus(commercetax.TaxTransactionStatus.Uncommitted);
             }
             response.setDocumentCode(docCode);
             response.setReferenceDocumentCode(request.referenceDocumentCode);
             response.setTaxType(type);
             response.setStatusDescription('statusDescription');
             if(request.sellerDetails.code == 'testSellerCode') {
                 response.setDescription('SellerCode fetched from TaxEngine entity');
             }
             else {
                 response.setDescription('description');
             }
            response.setEffectiveDate(system.now());
            if(request.transactionDate == null) {
               response.setTransactionDate(system.now());
            } else {
               response.setTransactionDate(request.transactionDate);
            }
            if(request.taxTransactionType == null) {
                response.setTaxTransactionType(commercetax.TaxTransactionType.Debit);
            } else {
                response.setTaxTransactionType(request.taxTransactionType);
            }
             if(request.currencyIsoCode == null || request.currencyIsoCode == '') {
                response.setCurrencyIsoCode('USD');
             } else {
                response.setCurrencyIsoCode(request.currencyIsoCode);
             }
             response.setReferenceEntityId(request.ReferenceEntityId);
}
```

- **[CalculateTaxResponse Methods](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_methods)**  
  Learn more about the available methods with the `CalculateTaxResponse` class.

## CalculateTaxResponse Methods

Learn more about the available methods with the `CalculateTaxResponse` class.

The `CalculateTaxResponse` class includes these
methods.

- **[setAddresses(addresses)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setAddresses)**  
  Sets the value of the Addresses field using the addresses contained in an instance of the AddressesResponse class.
- **[setAmountDetails(amountDetails)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setAmountDetails)**  
  Sets the value of the AmountDetails field using an instance of `AmountDetailsResponse`.
- **[setCurrencyIsoCode(currencyIsoCode)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setCurrencyIsoCode)**  
  Sets the value of the CurrencyIsoCode field of the `CalculateTaxResponse` object.
- **[setDescription(dscptn)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setDescription)**  
  Sets the value of the Description field of the `CalculateTaxResponse` object.
- **[setDocumentCode(documentCode)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setDocumentCode)**  
  Sets the value of the DocumentCode field of the `CalculateTaxResponse` object.
- **[setEffectiveDate(effectiveDate)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setEffectiveDate)**  
  Sets the value of the EffectiveDate field of the `CalculateTaxResponse` object.
- **[setLineItems(lineItems)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setLineItems)**  
  Sets the value of the LineItems field of the `CalculateTaxResponse` object.
- **[setReferenceDocumentCode(referenceDocumentCode)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setReferenceDocumentCode)**  
  Sets the value of the ReferenceDocumentCode field of the `CalculateTaxResponse` object.
- **[setReferenceEntityId(referenceEntityId)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setReferenceEntityId)**  
  Sets the value of the ReferenceEntityId field of the `CalculateTaxResponse` object.
- **[setStatus(status)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setStatus)**  
  Sets the value of the Status field of the `CalculateTaxResponse` object.
- **[setStatusDescription(statusDescription)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setStatusDescription)**  
  Sets the value of the StatusDescription field of the `CalculateTaxResponse` object.
- **[setTaxTransactionId(taxTrxnId)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setTaxTransactionId)**  
  Sets the value of the TaxTransactionId field of the `CalculateTaxResponse` object.
- **[setTaxTransactionType(taxTransactionType)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setTaxTransactionType)**  
  Sets the value of the TaxTransactionType field of the `CalculateTaxResponse` object.
- **[setTaxType(taxType)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setTaxType)**  
  Sets the value of the TaxType field of the `CalculateTaxResponse` object.
- **[setTransactionDate(transactionDate)](./apex_class_commercetax_CalculateTaxResponse.htm.md#apex_commercetax_CalculateTaxResponse_setTransactionDate)**  
  Sets the value of the TransactionDate field of the `CalculateTaxResponse` object.

### setAddresses(addresses)

Sets the value of the Addresses field using the addresses contained
in an instance of the [AddressesResponse](./apex_class_commercetax_AddressesResponse.htm.md#apex_class_commercetax_AddressesResponse "Sets the tax address fields based on a response from the external tax engine. Contains setter methods for the Ship From, Ship To, and Sold To addresses.")
class.

#### Signature

`global void setAddresses(commercetax.AddressesResponse
addresses)`

#### Parameters

addresses
:   Type: [AddressesResponse](./apex_class_commercetax_AddressesResponse.htm.md#apex_class_commercetax_AddressesResponse "Sets the tax address fields based on a response from the external tax engine. Contains setter methods for the Ship From, Ship To, and Sold To addresses.")
:   Contains Ship To, Ship From, and Sold To addresses.

#### Return Value

Type: void

### setAmountDetails(amountDetails)

Sets the value of the AmountDetails field using an instance of [`AmountDetailsResponse`](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_class_commercetax_AmountDetailsResponse "Sets tax amount fields based on a response from the external tax engine.").

#### Signature

`global void setAmountDetails(commercetax.AmountDetailsResponse
amountDetails)`

#### Parameters

amountDetails
:   Type: [AmountDetailsResponse](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_class_commercetax_AmountDetailsResponse "Sets tax amount fields based on a response from the external tax engine.")
:   The tax amount details for a line item on which tax was calculated.

#### Return Value

Type: void

### setCurrencyIsoCode(currencyIsoCode)

Sets the value of the CurrencyIsoCode field of the `CalculateTaxResponse` object.

#### Signature

`global void
setCurrencyIsoCode(String
currencyIsoCode)`

#### Parameters

currencyIsoCode
:   Type: String
:   Three-letter ISO 4217 currency code associated with a tax object.

#### Return Value

Type: void

### setDescription(dscptn)

Sets the value of the Description field of the `CalculateTaxResponse` object.

#### Signature

`global void
setDescription(String
dscptn)`

#### Parameters

dscptn
:   Type: String
:   Optional description for providing more information about the calculate tax
    response.

#### Return Value

Type: void

### setDocumentCode(documentCode)

Sets the value of the DocumentCode field of the `CalculateTaxResponse` object.

#### Signature

`global void
setDocumentCode(String
documentCode)`

#### Parameters

documentCode
:   Type: String
:   Code for a tax document that’s created by the tax engine for the calculation
    process.

#### Return Value

Type: void

### setEffectiveDate(effectiveDate)

Sets the value of the EffectiveDate field of the `CalculateTaxResponse` object.

#### Signature

`global void
setEffectiveDate(Datetime
effectiveDate)`

#### Parameters

effectiveDate
:   Type: Datetime
:   The date a tax calculation action takes effect. This parameter is optional and is
    provided only for recordkeeping purpose. Additionally, this parameter is used to
    determine the tax rates or rules and overrides the transaction date. For example, if the
    tax calculation request is placed on January 3 and the transaction date is January 1,
    you can set the effective date as January 1.

#### Return Value

Type: void

### setLineItems(lineItems)

Sets the value of the LineItems field of the `CalculateTaxResponse` object.

#### Signature

`global void setLineItems(List<commercetax.LineItemResponse>
lineItems)`

#### Parameters

lineItems
:   Type: List<[LineItemResponse](./apex_class_commercetax_LineItemResponse.htm.md#apex_class_commercetax_LineItemResponse "Response class that stores details of a list of one or more line items on which the tax engine has calculated tax.")>
:   Response object that the tax adapter populates from the response of the external tax
    engine.

#### Return Value

Type: void

### setReferenceDocumentCode(referenceDocumentCode)

Sets the value of the ReferenceDocumentCode field of the `CalculateTaxResponse` object.

#### Signature

`global void
setReferenceDocumentCode(String
referenceDocumentCode)`

#### Parameters

referenceDocumentCode
:   Type: String
:   Code for a reference document used in the tax calculation process.

#### Return Value

Type: void

### setReferenceEntityId(referenceEntityId)

Sets the value of the ReferenceEntityId field of the `CalculateTaxResponse` object.

#### Signature

`global void
setReferenceEntityId(String
referenceEntityId)`

#### Parameters

referenceEntityId
:   Type: String
:   ID of an entity related to the line items submitted for tax calculation. For example,
    if order items were sent for tax calculation, you could use the ID of their parent
    order.

#### Return Value

Type: void

### setStatus(status)

Sets the value of the Status field of the `CalculateTaxResponse` object.

#### Signature

`global void setStatus(commercetax.TaxTransactionStatus
status)`

#### Parameters

status
:   Type: [TaxTransactionStatus](./apex_enum_commercetax_TaxTransactionStatus.htm.md "Shows whether the tax transaction has been committed or uncommitted.")
:   Indicates whether a tax transaction has been committed.

#### Return Value

Type: void

### setStatusDescription(statusDescription)

Sets the value of the StatusDescription field of the `CalculateTaxResponse` object.

#### Signature

`global void
setStatusDescription(String
statusDescription)`

#### Parameters

statusDescription
:   Type: String
:   Optional value for providing more information about a tax transaction's status.

#### Return Value

Type: void

### setTaxTransactionId(taxTrxnId)

Sets the value of the TaxTransactionId field of the `CalculateTaxResponse` object.

#### Signature

`public void
setTaxTransactionId(String
taxTrxnId)`

#### Parameters

taxTrxnId
:   Type: String
:   The ID of the
    Salesforce
    tax transaction entity that stores information about the tax
    calculation transaction.

#### Return Value

Type: void

### setTaxTransactionType(taxTransactionType)

Sets the value of the TaxTransactionType field of the `CalculateTaxResponse` object.

#### Signature

`global void setTaxTransactionType(commercetax.TaxTransactionType
taxTransactionType)`

#### Parameters

taxTransactionType
:   Type: [TaxTransactionType](./apex_enum_commercetax_TaxTransactionType.htm.md "Shows whether the tax transaction is for a credit or debit transaction.")
:   Whether the tax transaction was for a credit, debit, or voided transaction.

#### Return Value

Type: void

### setTaxType(taxType)

Sets the value of the TaxType field of the `CalculateTaxResponse` object.

#### Signature

`global void setTaxType(commercetax.CalculateTaxType
taxType)`

#### Parameters

taxType
:   Type: [CalculateTaxType](./apex_enum_commercetax_CalculateTaxType.htm.md "Shows whether a tax calculation request is for estimated or actual tax.")
:   Indicates whether a tax calculation request is for estimated or actual tax.

#### Return Value

Type: void

### setTransactionDate(transactionDate)

Sets the value of the TransactionDate field of the `CalculateTaxResponse` object.

#### Signature

`global void
setTransactionDate(Datetime
transactionDate)`

#### Parameters

transactionDate
:   Type: Datetime
:   The date that the tax transaction occurred.

#### Return Value

Type: void
