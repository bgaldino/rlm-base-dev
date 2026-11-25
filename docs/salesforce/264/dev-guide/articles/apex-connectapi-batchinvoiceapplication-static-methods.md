---
page_id: apex-connectapi-batchinvoiceapplication-static-methods
title: BatchInvoiceApplication Class
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-batchinvoiceapplication-static-methods.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-connect-api-namespace
legacy_page_id: apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm
fetched_at: 2026-11-25
---

# BatchInvoiceApplication Class

Update a batch of invoices from Draft to Posted status for a credit memo application. by using the BatchInvoiceApplication class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_classes_connect_api.htm)

## BatchInvoiceApplication Methods

These methods are for `BatchInvoiceApplication`. All methods are static.

- 

**[triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)](#triggerinvoicebatchdrafttopostedinvoicebatchrunid)**

Update a batch of invoices from Draft to Posted status for a credit memo application.

### triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)

Update a batch of invoices from Draft to Posted status for a credit memo application.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.InvoiceBatchDraftToPostedResult triggerInvoiceBatchDraftToPosted(String invoiceBatchRunId)`

#### Parameters

***invoiceBatchRunId***

Type: String

ID of the invoice batch run record that creates the draft invoices.

#### Return Value

Type: [`ConnectApi.InvoiceBatchDraftToPostedResult`](./apex-connectapi-output-invoice-batch-draft-to-posted-output.md)

#### Usage

You need the Billing Operations User permission set to use this method.

This method posts the draft invoices and changes the status of the invoices from `Draft` to `Posted`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-batchinvoiceapplication-static-methods.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
