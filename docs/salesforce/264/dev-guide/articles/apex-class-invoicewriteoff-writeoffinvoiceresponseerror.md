---
page_id: apex-class-invoicewriteoff-writeoffinvoiceresponseerror
title: WriteOffInvoiceResponseError Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponseerror.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-invoicewriteoff
legacy_page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponseError.htm
fetched_at: 2026-11-25
---

# WriteOffInvoiceResponseError Class

Contains properties to store the error response that’s associated with a request to write off a posted invoice.

## Namespace

[InvoiceWriteOff](./apex-namespace-invoicewriteoff.md)

- 

**[WriteOffInvoiceResponseError Constructors](#writeoffinvoiceresponseerror-constructors)**

Learn more about the constructors available with the WriteOffInvoiceResponseError class.

- 

**[WriteOffInvoiceResponseError Properties](#writeoffinvoiceresponseerror-properties)**

Learn more about the properties available with the WriteOffInvoiceResponseError class.

## WriteOffInvoiceResponseError Constructors

Learn more about the constructors available with the WriteOffInvoiceResponseError class.

The `WriteOffInvoiceResponseError` class includes these constructors.

- 

**[WriteOffInvoiceResponseError(errorCode, errorMessage)](#writeoffinvoiceresponseerrorerrorcode-errormessage)**

Initializes the WriteOffInvoiceResponseError class that stores the error response that’s associated with a request to write off a posted invoice.

### WriteOffInvoiceResponseError(errorCode, errorMessage)

Initializes the WriteOffInvoiceResponseError class that stores the error response that’s associated with a request to write off a posted invoice.

#### Signature

`public WriteOffInvoiceResponseError(String errorCode, String errorMessage)`

#### Parameters

***errorCode***

Type: String

Code that represents the error.

***errorMessage***

Type: String

Message that describes the error.

## WriteOffInvoiceResponseError Properties

Learn more about the properties available with the WriteOffInvoiceResponseError class.

The `WriteOffInvoiceResponseError` class includes these properties.

- 

**[errorCode](#errorcode)**

Get the error code details.

- 

**[errorMessage](#errormessage)**

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponseerror.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
