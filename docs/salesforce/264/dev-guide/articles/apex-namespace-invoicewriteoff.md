---
page_id: apex-namespace-invoicewriteoff
title: InvoiceWriteOff Namespace
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-invoicewriteoff.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-reference
legacy_page_id: apex_namespace_InvoiceWriteOff.htm
fetched_at: 2026-11-25
---

# InvoiceWriteOff Namespace

Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.

The `InvoiceWriteOff` namespace includes these classes.

## Usage

You need the Billing Operations User or Credit Memo Operations User permission set to access this namespace.

- 

**[WriteOffInvoiceInput Class](./apex-class-invoicewriteoff-writeoffinvoiceinput.md#writeoffinvoiceinput-class)**

Contains invoice details that are used for the request to write off an invoice.

- 

**[WriteOffInvoiceInputList Class](./apex-class-invoicewriteoff-writeoffinvoiceinputlist.md#writeoffinvoiceinputlist-class)**

Contains invoice details to write off a list of posted invoices.

- 

**[WriteOffInvoiceResponse Class](./apex-class-invoicewriteoff-writeoffinvoiceresponse.md#writeoffinvoiceresponse-class)**

Contains properties to store the response details to the request to write off a posted invoice.

- 

**[WriteOffInvoiceResponseError Class](./apex-class-invoicewriteoff-writeoffinvoiceresponseerror.md#writeoffinvoiceresponseerror-class)**

Contains properties to store the error response that’s associated with a request to write off a posted invoice.

- 

**[WriteOffInvoiceResponseList Class](./apex-class-invoicewriteoff-writeoffinvoiceresponselist.md#writeoffinvoiceresponselist-class)**

Contains properties to store the response details of the list of invoices that are written off.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-namespace-invoicewriteoff.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
