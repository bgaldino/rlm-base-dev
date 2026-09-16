---
page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm
title: WriteOffInvoiceResponse Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# WriteOffInvoiceResponse Class

Contains properties to store the response details to the request to write off a posted
    invoice.

## Namespace

[InvoiceWriteOff](./apex_namespace_InvoiceWriteOff.htm.md)

- 
**[WriteOffInvoiceResponse Constructors](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_constructors)**  

Learn more about the constructors available with the WriteOffInvoiceResponse     class.

- 
**[WriteOffInvoiceResponse Properties](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_properties)**  

Learn more about the properties available with the WriteOffInvoiceResponse     class.

  

## WriteOffInvoiceResponse Constructors

  
  
  
Learn more about the constructors available with the WriteOffInvoiceResponse
    class.

    
      

The `WriteOffInvoiceResponse` class includes these
        constructors.

    

- 
**[WriteOffInvoiceResponse(errors, invoiceId, requestIdentifier, success)](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_ctor)**  

Initializes the WriteOffInvoiceResponse class that stores the response details to the     request to write off a posted invoice.

### WriteOffInvoiceResponse(errors, invoiceId, requestIdentifier, success)

Initializes the WriteOffInvoiceResponse class that stores the response details to the
    request to write off a posted invoice.

#### Signature

`public WriteOffInvoiceResponse(InvoiceWriteOff.WriteOffInvoiceResponseError errors, String invoiceId, String requestIdentifier, Boolean success)`

#### Parameters

**errors**

: Type: [InvoiceWriteOff.WriteOffInvoiceResponseError](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError)

: 

If the request fails, this property contains a list of
                  errors.

**invoiceId**

: Type: String

: 

ID of the invoice record that's written off.

**requestIdentifier**

: Type: String

: 

If the request is successful, this property contains an asynchronous API
                  request identifier for an invoice ID.

**success**

: Type: Boolean

: 

Indicates whether the invoice write-off request was successful
                    (`true`) or not (`false`).

  

## WriteOffInvoiceResponse Properties

  
  
  
Learn more about the properties available with the WriteOffInvoiceResponse
    class.

    
      

The `WriteOffInvoiceResponse` class includes these
        properties.

    

- 
**[errors](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_errors)**  

Get the list of errors if the request to write off posted invoices fails.

- 
**[invoiceId](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_invoiceId)**  

Get the ID of the invoice record that's written off.

- 
**[requestIdentifier](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_requestIdentifier)**  

Get the identifier of the asynchronous API request for an invoice ID if the request is     successful.

- 
**[success](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm.md#apex_InvoiceWriteOff_WriteOffInvoiceResponse_success)**  

Get the request status of the invoice write-off request.

### errors

Get the list of errors if the request to write off posted invoices fails.

#### Signature

`public InvoiceWriteOff.WriteOffInvoiceResponseError errors {get; set;}`

#### Property Value

Type: [InvoiceWriteOff.WriteOffInvoiceResponseError](./apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm.md#apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError)

### invoiceId

  
Get the ID of the invoice record that's written off.

#### Signature

`public String invoiceId {get; set;}`

#### Property Value

Type: String

### requestIdentifier

Get the identifier of the asynchronous API request for an invoice ID if the request is
    successful.

#### Signature

`public String requestIdentifier {get; set;}`

#### Property Value

Type: String

### success

Get the request status of the invoice write-off request.

#### Signature

`public Boolean success {get; set;}`

#### Property Value

Type: Boolean
