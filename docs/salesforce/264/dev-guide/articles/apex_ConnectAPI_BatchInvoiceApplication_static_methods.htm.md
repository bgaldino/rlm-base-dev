---
page_id: apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm
title: BatchInvoiceApplication Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-11-23
---

# BatchInvoiceApplication Class

Update a batch of invoices from Draft to Posted status for a credit memo application. by
using the BatchInvoiceApplication class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_classes_connect_api.htm "HTML (New Window)")

## BatchInvoiceApplication Methods

These methods are for `BatchInvoiceApplication`.
All methods are static.

- **[triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)](./apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm.md#apex_ConnectAPI_BatchInvoiceApplication_triggerInvoiceBatchDraftToPosted_1)**  
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

**invoiceBatchRunId**

Type: String

ID of the invoice batch run record that creates the draft invoices.

#### Return Value

Type: [`ConnectApi.InvoiceBatchDraftToPostedResult`](./apex_connectapi_output_invoice_batch_draft_to_posted_output.htm.md "Output representation of the batch update details of the invoices from Draft to Posted status.")

#### Usage

You need the Billing Operations User permission set to use this method.

This method posts the draft invoices and changes the status of the invoices from `Draft` to `Posted`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
