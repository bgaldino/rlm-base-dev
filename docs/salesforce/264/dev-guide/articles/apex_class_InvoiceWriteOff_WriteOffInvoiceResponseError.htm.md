---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm
title: WriteOffInvoiceResponseError Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# WriteOffInvoiceResponseError Class

Contains properties to store the error response that's associated with a request to write
    off a posted invoice.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md)

- 
**[WriteOffInvoiceResponseError Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseError_constructors)**  

Learn more about the constructors available with the WriteOffInvoiceResponseError     class.

- 
**[WriteOffInvoiceResponseError Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseError_properties)**  

Learn more about the properties available with the WriteOffInvoiceResponseError     class.

  

## WriteOffInvoiceResponseError Constructors

  
  
  
Learn more about the constructors available with the WriteOffInvoiceResponseError
    class.

    
      

The `WriteOffInvoiceResponseError` class includes these
        constructors.

    

- 
**[WriteOffInvoiceResponseError(errorCode, errorMessage)](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseError_ctor)**  

Initializes the WriteOffInvoiceResponseError class that stores the error response that's     associated with a request to write off a posted invoice.

### WriteOffInvoiceResponseError(errorCode, errorMessage)

Initializes the WriteOffInvoiceResponseError class that stores the error response that's
    associated with a request to write off a posted invoice.

#### Signature

`public WriteOffInvoiceResponseError(String errorCode, String errorMessage)`

#### Parameters

**errorCode**

: Type: String

: 

Code that represents the error.

**errorMessage**

: Type: String

: 

Message that describes the error.

## WriteOffInvoiceResponseError Properties

  
Learn more about the properties available with the WriteOffInvoiceResponseError
    class.

    
      

The `WriteOffInvoiceResponseError` class includes these
        properties.

    

- 
**[errorCode](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseError_errorCode)**  

Get the error code details.

- 
**[errorMessage](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponseError_errorMessage)**  

Get the error message details.

### errorCode

Get the error code details.

#### Signature

`public String errorCode {get; set;}`

#### Property Value

Type: String

### errorMessage

Get the error message details.

#### Signature

`public String errorMessage {get; set;}`

#### Property Value

Type: String
