---
page_id: apex-class-invoicewriteoff-writeoffinvoiceinputlist
title: WriteOffInvoiceInputList Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceinputlist.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: apex-namespace-invoicewriteoff
legacy_page_id: apex_class_InvoiceWriteOff_WriteOffInvoiceInputList.htm
fetched_at: 2026-11-25
---

# WriteOffInvoiceInputList Class

Contains invoice details to write off a list of posted invoices.

## Namespace

[InvoiceWriteOff](./apex-namespace-invoicewriteoff.md)

- 

**[WriteOffInvoiceInputList Constructors](#writeoffinvoiceinputlist-constructors)**

Learn more about the constructors available with the WriteOffInvoiceInputList class.

- 

**[WriteOffInvoiceInputList Properties](#writeoffinvoiceinputlist-properties)**

Learn more about the properties available with the WriteOffInvoiceInputList class.

## WriteOffInvoiceInputList Constructors

Learn more about the constructors available with the WriteOffInvoiceInputList class.

The `WriteOffInvoiceInputList` class includes these constructors.

- 

**[WriteOffInvoiceInputList(writeOffInvoiceInputList)](#writeoffinvoiceinputlistwriteoffinvoiceinputlist)**

Initializes the WriteOffInvoiceInputList class that stores the details of invoices that you want to write off.

- 

**[WriteOffInvoiceInputList()](#writeoffinvoiceinputlist)**

Initializes the WriteOffInvoiceInputList class.

### WriteOffInvoiceInputList(writeOffInvoiceInputList)

Initializes the WriteOffInvoiceInputList class that stores the details of invoices that you want to write off.

#### Signature

`public WriteOffInvoiceInputList(List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList)`

#### Parameters

***writeOffInvoiceInputList***

Type: List<I[nvoiceWriteOff.WriteOffInvoiceInput](./apex-class-invoicewriteoff-writeoffinvoiceinput.md#writeoffinvoiceinput-class)>

Input representation of the request to write off a list of posted invoices.

### WriteOffInvoiceInputList()

Initializes the WriteOffInvoiceInputList class.

#### Signature

`public WriteOffInvoiceInputList()`

## WriteOffInvoiceInputList Properties

Learn more about the properties available with the WriteOffInvoiceInputList class.

The `WriteOffInvoiceInputList` class includes these properties.

- 

**[writeOffInvoiceInputList](#writeoffinvoiceinputlist)**

Input representation of the request to write off a list of posted invoices.

### writeOffInvoiceInputList

Input representation of the request to write off a list of posted invoices.

#### Signature

`public List<InvoiceWriteOff.WriteOffInvoiceInput> writeOffInvoiceInputList {get; set;}`

#### Property Value

Type: List<[nvoiceWriteOff.WriteOffInvoiceInput](./apex-class-invoicewriteoff-writeoffinvoiceinput.md#writeoffinvoiceinput-class)>

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-class-invoicewriteoff-writeoffinvoiceinputlist.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
