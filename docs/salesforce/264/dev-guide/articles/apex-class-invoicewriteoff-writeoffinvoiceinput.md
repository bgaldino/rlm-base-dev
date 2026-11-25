---
page_id: apex-class-invoicewriteoff-writeoffinvoiceinput
title: WriteOffInvoiceInput Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceinput.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-invoicewriteoff
legacy_page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceInput.htm
fetched_at: 2026-11-25
---

# WriteOffInvoiceInput Class

Contains invoice details that are used for the request to write off an invoice.

## Namespace

[InvoiceWriteOff](./apex-namespace-invoicewriteoff.md)

- 

**[WriteOffInvoiceInput Constructors](#writeoffinvoiceinput-constructors)**

Learn more about the constructors available with the WriteOffInvoiceInput class.

- 

**[WriteOffInvoiceInput Properties](#writeoffinvoiceinput-properties)**

Learn more about the properties available with the WriteOffInvoiceInput class.

## WriteOffInvoiceInput Constructors

Learn more about the constructors available with the WriteOffInvoiceInput class.

The `WriteOffInvoiceInput` class includes these constructors.

- 

**[WriteOffInvoiceInput(invoiceId, reasonCode, reason)](#writeoffinvoiceinputinvoiceid-reasoncode-reason)**

Initializes the WriteOffInvoiceInput class that stores the invoice details and reason for writing off invoices.

- 

**[WriteOffInvoiceInput()](#writeoffinvoiceinput)**

Initializes the WriteOffInvoiceInput class.

### WriteOffInvoiceInput(invoiceId, reasonCode, reason)

Initializes the WriteOffInvoiceInput class that stores the invoice details and reason for writing off invoices.

#### Signature

`public WriteOffInvoiceInput(String invoiceId, String reasonCode, String reason)`

#### Parameters

***invoiceId***

Type: String

ID of the invoice record that you want to write off.

***reasonCode***

Type: String

Code that categorizes the write-off reason. For example, if the reason for the invoice write-off is a disputed amount, the reason code can be Disputed Amount (DA).

***reason***

Type: String

Reason for writing off invoices.

### WriteOffInvoiceInput()

Initializes the WriteOffInvoiceInput class.

#### Signature

`public WriteOffInvoiceInput()`

## WriteOffInvoiceInput Properties

Learn more about the properties available with the WriteOffInvoiceInput class.

The `WriteOffInvoiceInput` class includes these properties.

- 

**[invoiceId](#invoiceid)**

Sets the ID of the invoice record that must be written off.

- 

**[reason](#reason)**

Sets the reason for writing off invoices.

- 

**[reasonCode](#reasoncode)**

Sets the code that categorizes the write-off reason.

### invoiceId

Sets the ID of the invoice record that must be written off.

#### Signature

`public String invoiceId {get; set;}`

#### Property Value

Type: String

### reason

Sets the reason for writing off invoices.

#### Signature

`public String reason {get; set;}`

#### Property Value

Type: String

### reasonCode

Sets the code that categorizes the write-off reason.

#### Signature

`public String reasonCode {get; set;}`

#### Property Value

Type: String

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceinput.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
