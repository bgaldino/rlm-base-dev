---
page_id: apex_class_commercetax_AbstractTransactionResponse.htm
title: AbstractTransactionResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_commercetax_AbstractTransactionResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: apex_namespace_commercetax.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

  

# AbstractTransactionResponse Class

  
  
  
Abstract class that contains methods for setting tax fields based on
      the external tax provider's response. Response classes that extend `AbstractTransactionResponse` inherit these methods.

    

## Namespace

[CommerceTax](./apex_namespace_commercetax.htm.md)

  

- 
**[AbstractTransactionResponse Methods](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_methods)**  

Learn more about the methods for AbstractTransactionResponse class.

  

## AbstractTransactionResponse Methods

  
  
  
Learn more about the methods for AbstractTransactionResponse class.

    
      

The `AbstractTransactionResponse` class includes these
        methods.

    

    
  

- 
**[setAddresses(addresses)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setAddresses)**  

Uses an instance of `AddressesResponse` to set the values of tax address fields.

- 
**[setAmountDetails(amountDetails)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setAmountDetails)**  

Uses an instance of `AmountDetailsResponse` to set tax amount fields such as exemption amount and tax       amount.

- 
**[setCurrencyIsoCode(currencyIsoCode)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setCurrencyIsoCode)**  

Sets the currencyIsoCode field.

- 
**[setCustomTaxAttributes(customTaxAttributes)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setCustomTaxAttributes)**  

Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax       response at the header level.

- 
**[setDescription(dscptn)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setDescription)**  

Sets the Description field.

- 
**[setDocumentCode(documentCode)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setDocumentCode)**  

Sets the DocumentCode field. Document codes are often used to       reference tax documents that the external tax engine uses in the tax calculation process.       Document code acts as a unique link to chain-related transactions, such as amendment or       refunds.

- 
**[setEffectiveDate(effectiveDate)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setEffectiveDate)**  

Sets the EffectiveDate field. Effective Date fields are optional       fields that store the date that a transaction takes effect. We provide these fields only for       recordkeeping purposes – for example, if you must report an effective date to an       external general ledger system. Salesforce doesn't use them to calculate any tax or payment       values.

- 
**[setLineItems(lineItems)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setLineItems)**  

Uses an instance of the `LineItemResponse` class to set a list of line items. Each line item represents an       item sent to an external tax engine for tax calculation.

- 
**[setReferenceDocumentCode(referenceDocumentCode)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setReferenceDocumentCode)**  

Sets the ReferenceDocumentCode field. Use this field to store the       code of an additional document used in the tax calculation process. For example, use this       field in case of a refund for a previously taxed purchase.

- 
**[setReferenceEntityId(referenceEntityId)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setReferenceEntityId)**  

Sets the ID of a reference entity. In Commerce Tax, a reference       entity represents a record related to the items sent to the external tax engine for tax       calculation. For example, if you sent order items for tax calculation, you could define the       parent order as the reference entity.

- 
**[setTaxTransactionId(taxTrxnId)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setTaxTransactionId)**  

Sets the TaxTransactionId field using the ID of a tax transaction       record. In Commerce Tax, a tax transaction record stores information about a specific tax       calculation process.

- 
**[setTransactionDate(transactionDate)](./apex_class_commercetax_AbstractTransactionResponse.htm.md#apex_commercetax_AbstractTransactionResponse_setTransactionDate)**  

Sets the TransactionDate field.

  

### setAddresses(addresses)

  
  
  
Uses an instance of `AddressesResponse` to set the values of tax address fields.

    

#### Signature

`global void setAddresses(commercetax.AddressesResponse
          addresses)`

    

#### Parameters

        
- 
**addresses**:

Type: [AddressesResponse](./apex_class_commercetax_AddressesResponse.htm.md#apex_class_commercetax_AddressesResponse)

Class that contains methods to set the Ship To, Ship From, and Sold To address
            information.

      

    

#### Return Value

Type: void

  

  

### setAmountDetails(amountDetails)

  
  
  
Uses an instance of `AmountDetailsResponse` to set tax amount fields such as exemption amount and tax
      amount.

    

#### Signature

`global void setAmountDetails(commercetax.AmountDetailsResponse
          amountDetails)`

    

#### Parameters

        
- 
**amountDetails**:

Type: [AmountDetailsResponse](./apex_class_commercetax_AmountDetailsResponse.htm.md#apex_class_commercetax_AmountDetailsResponse)

Class that contains methods to set the tax exemption amount, tax amount, total amount,
            and total amount with tax.

      

    

#### Return Value

Type: void

  

  

### setCurrencyIsoCode(currencyIsoCode)

  
  
  
Sets the currencyIsoCode field.

    

#### Signature

`global void
          setCurrencyIsoCode(String
      currencyIsoCode)`

    

#### Parameters

        
- 
**currencyIsoCode**:

Type: String

Three-letter ISO 4217 currency code associated with a tax object.

      

    

#### Return Value

Type: void

  

  

### setCustomTaxAttributes(customTaxAttributes)

  
  
  
Uses an instance of `CustomTaxAttributesResponse` class to include additional attributes in the tax
      response at the header level.

    

#### Signature

      
      

`global void
          setCustomTaxAttributes(commercetax.CustomTaxAttributesResponse
          customTaxAttributes)`

      
    

    

#### Parameters

      
      
        
- 
**customTaxAttributes**:

Type: [CustomTaxAttributesResponse](./apex_class_commercetax_CustomTaxAttributesResponse.htm.md#apex_class_commercetax_CustomTaxAttributesResponse)

Additional

data or custom attributes to include in the tax response.

      

    

    

#### Return Value

      
      

Type: void

    

  

  

### setDescription(dscptn)

  
  
  
Sets the Description field.

    

#### Signature

`global void
          setDescription(String
      dscptn)`

    

#### Parameters

        
- 
**dscptn**:

Type: String

Optional field for providing additional information about a record.

      

    

#### Return Value

Type: void

  

  

### setDocumentCode(documentCode)

  
  
  
Sets the DocumentCode field. Document codes are often used to
      reference tax documents that the external tax engine uses in the tax calculation process.
      Document code acts as a unique link to chain-related transactions, such as amendment or
      refunds.

    

#### Signature

`global void
          setDocumentCode(String
      documentCode)`

    

#### Parameters

        
- 
**documentCode**:

Type: String

Code

for a tax document used in the tax calculation process.

      

    

#### Return Value

Type: void

  

  

### setEffectiveDate(effectiveDate)

  
  
  
Sets the EffectiveDate field. Effective Date fields are optional
      fields that store the date that a transaction takes effect. We provide these fields only for
      recordkeeping purposes – for example, if you must report an effective date to an
      external general ledger system. Salesforce doesn't use them to calculate any tax or payment
      values.

    

#### Signature

`global void
          setEffectiveDate(Datetime
      effectiveDate)`

    

#### Parameters

        
- 
**effectiveDate**:

Type: Datetime

Optional field that stores the date that a transaction takes effect.

      

    

#### Return Value

Type: void

  

  

### setLineItems(lineItems)

  
  
  
Uses an instance of the `LineItemResponse` class to set a list of line items. Each line item represents an
      item sent to an external tax engine for tax calculation.

    

#### Signature

`global void setLineItems(List<commercetax.LineItemResponse>
          lineItems)`

    

#### Parameters

        
- 
**lineItems**:

Type: List<[LineItemResponse](./apex_class_commercetax_LineItemResponse.htm.md#apex_class_commercetax_LineItemResponse)>

A list of line items sent to an external tax engine for tax calculation.

      

    

#### Return Value

Type: void

  

  

### setReferenceDocumentCode(referenceDocumentCode)

  
  
  
Sets the ReferenceDocumentCode field. Use this field to store the
      code of an additional document used in the tax calculation process. For example, use this
      field in case of a refund for a previously taxed purchase.

    

#### Signature

`global void
          setReferenceDocumentCode(String
      referenceDocumentCode)`

    

#### Parameters

        
- 
**referenceDocumentCode**:

Type: String

The code for a document used in the tax calculation process.

      

    

#### Return Value

Type: void

  

  

### setReferenceEntityId(referenceEntityId)

  
  
  
Sets the ID of a reference entity. In Commerce Tax, a reference
      entity represents a record related to the items sent to the external tax engine for tax
      calculation. For example, if you sent order items for tax calculation, you could define the
      parent order as the reference entity.

    

#### Signature

`global void
          setReferenceEntityId(String
      referenceEntityId)`

    

#### Parameters

        
- 
**referenceEntityId**:

Type: String

ID of a record related to the items sent for tax calculation.

      

    

#### Return Value

Type: void

  

  

### setTaxTransactionId(taxTrxnId)

  
  
  
Sets the TaxTransactionId field using the ID of a tax transaction
      record. In Commerce Tax, a tax transaction record stores information about a specific tax
      calculation process.

    

#### Signature

`global void
          setTaxTransactionId(String
      taxTrxnId)`

    

#### Parameters

        
- 
**taxTrxnId**:

Type: String

The ID of a tax transaction record in Commerce Tax.

      

    

#### Return Value

Type: void

  

  

### setTransactionDate(transactionDate)

  
  
  
Sets the TransactionDate field.

    

#### Signature

`global void
          setTransactionDate(Datetime
      transactionDate)`

    

#### Parameters

        
- 
**transactionDate**:

Type: Datetime

Date that a tax transaction occurred.

      

    

#### Return Value

Type: void
