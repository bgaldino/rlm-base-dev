---
page_id: apex-class-invoicewriteoff-writeoffinvoiceresponselist
title: WriteOffInvoiceResponseList Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponselist.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-invoicewriteoff
legacy_page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceResponseList.htm
fetched_at: 2026-11-25
---

# WriteOffInvoiceResponseList Class

Contains properties to store the response details of the list of invoices that are written off.

## Namespace

[InvoiceWriteOff](./apex-namespace-invoicewriteoff.md)

- 

**[WriteOffInvoiceResponseList Constructors](#writeoffinvoiceresponselist-constructors)**

Learn more about the constructors available with the WriteOffInvoiceResponseList class.

- 

**[WriteOffInvoiceResponseList Properties](#writeoffinvoiceresponselist-properties)**

Learn more about the properties available with the WriteOffInvoiceResponseList class.

## WriteOffInvoiceResponseList Constructors

Learn more about the constructors available with the WriteOffInvoiceResponseList class.

The `WriteOffInvoiceResponseList` class includes these constructors.

- 

**[WriteOffInvoiceResponseList(writeOffInvoiceResponseList)](#writeoffinvoiceresponselistwriteoffinvoiceresponselist)**

Initializes the WriteOffInvoiceResponseList class that stores the response details of the list of invoices that are written off.

- 

**[WriteOffInvoiceResponseList()](#writeoffinvoiceresponselist)**

Initializes the WriteOffInvoiceResponseList class.

### WriteOffInvoiceResponseList(writeOffInvoiceResponseList)

Initializes the WriteOffInvoiceResponseList class that stores the response details of the list of invoices that are written off.

#### Signature

`public WriteOffInvoiceResponseList(List<InvoiceWriteOff.WriteOffInvoiceResponse> writeOffInvoiceResponseList)`

#### Parameters

***writeOffInvoiceResponseList***

Type: List<[InvoiceWriteOff.WriteOffInvoiceResponse](./apex-class-invoicewriteoff-writeoffinvoiceresponse.md#writeoffinvoiceresponse-class)>

Details of the invoices for which the write-off process is initiated.

### WriteOffInvoiceResponseList()

Initializes the WriteOffInvoiceResponseList class.

#### Signature

`public WriteOffInvoiceResponseList()`

## WriteOffInvoiceResponseList Properties

Learn more about the properties available with the WriteOffInvoiceResponseList class.

The `WriteOffInvoiceResponseList` class includes these properties.

- 

**[writeOffInvoiceResponseList](#writeoffinvoiceresponselist)**

Get the details of the invoices for which the write-off posted invoice process is initiated.

### writeOffInvoiceResponseList

Get the details of the invoices for which the write-off posted invoice process is initiated.

#### Signature

`public List<InvoiceWriteOff.WriteOffInvoiceResponse> writeOffInvoiceResponseList {get; set;}`

#### Property Value

Type: List<[InvoiceWriteOff.WriteOffInvoiceResponse](./apex-class-invoicewriteoff-writeoffinvoiceresponse.md#writeoffinvoiceresponse-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceresponselist.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
