---
page_id: apex-class-invoicewriteoff-writeoffinvoiceresponse
title: WriteOffInvoiceResponse Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponse.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-invoicewriteoff
legacy_page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponse.htm
fetched_at: 2026-11-25
---

# WriteOffInvoiceResponse Class

Contains properties to store the response details to the request to write off a posted invoice.

## Namespace

[InvoiceWriteOff](./apex-namespace-invoicewriteoff.md)

- 

**[WriteOffInvoiceResponse Constructors](#writeoffinvoiceresponse-constructors)**

Learn more about the constructors available with the WriteOffInvoiceResponse class.

- 

**[WriteOffInvoiceResponse Properties](#writeoffinvoiceresponse-properties)**

Learn more about the properties available with the WriteOffInvoiceResponse class.

## WriteOffInvoiceResponse Constructors

Learn more about the constructors available with the WriteOffInvoiceResponse class.

The `WriteOffInvoiceResponse` class includes these constructors.

- 

**[WriteOffInvoiceResponse(errors, invoiceId, requestIdentifier, success)](#writeoffinvoiceresponseerrors-invoiceid-requestidentifier-success)**

Initializes the WriteOffInvoiceResponse class that stores the response details to the request to write off a posted invoice.

### WriteOffInvoiceResponse(errors, invoiceId, requestIdentifier, success)

Initializes the WriteOffInvoiceResponse class that stores the response details to the request to write off a posted invoice.

#### Signature

`public WriteOffInvoiceResponse(InvoiceWriteOff.WriteOffInvoiceResponseError errors, String invoiceId, String requestIdentifier, Boolean success)`

#### Parameters

***errors***

Type: [InvoiceWriteOff.WriteOffInvoiceResponseError](./apex-class-invoicewriteoff-writeoffinvoiceresponseerror.md#writeoffinvoiceresponseerror-class)

If the request fails, this property contains a list of errors.

***invoiceId***

Type: String

ID of the invoice record that’s written off.

***requestIdentifier***

Type: String

If the request is successful, this property contains an asynchronous API request identifier for an invoice ID.

***success***

Type: Boolean

Indicates whether the invoice write-off request was successful (`true`) or not (`false`).

## WriteOffInvoiceResponse Properties

Learn more about the properties available with the WriteOffInvoiceResponse class.

The `WriteOffInvoiceResponse` class includes these properties.

- 

**[errors](#errors)**

Get the list of errors if the request to write off posted invoices fails.

- 

**[invoiceId](#invoiceid)**

Get the ID of the invoice record that’s written off.

- 

**[requestIdentifier](#requestidentifier)**

Get the identifier of the asynchronous API request for an invoice ID if the request is successful.

- 

**[success](#success)**

Get the request status of the invoice write-off request.

### errors

Get the list of errors if the request to write off posted invoices fails.

#### Signature

`public InvoiceWriteOff.WriteOffInvoiceResponseError errors {get; set;}`

#### Property Value

Type: [InvoiceWriteOff.WriteOffInvoiceResponseError](./apex-class-invoicewriteoff-writeoffinvoiceresponseerror.md#writeoffinvoiceresponseerror-class)

### invoiceId

Get the ID of the invoice record that’s written off.

#### Signature

`public String invoiceId {get; set;}`

#### Property Value

Type: String

### requestIdentifier

Get the identifier of the asynchronous API request for an invoice ID if the request is successful.

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponse.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
