---
page_id: apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm
title: BatchInvoiceApplication Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# BatchInvoiceApplication Class

Update a batch of invoices from Draft to Posted status for a credit memo application. by
using the BatchInvoiceApplication class.

## Namespace

ConnectApi

## BatchInvoiceApplication Methods

These methods are for `BatchInvoiceApplication`.
All methods are static.

- **[triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)](./apex_ConnectAPI_BatchInvoiceApplication_static_methods.htm.md#apex_ConnectAPI_BatchInvoiceApplication_triggerInvoiceBatchDraftToPosted_1)**  
  Update a batch of invoices from Draft to Posted status for a credit memo application.

### triggerInvoiceBatchDraftToPosted(invoiceBatchRunId)

Update a batch of invoices from Draft to Posted status for a credit memo
application.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.InvoiceBatchDraftToPostedResult
triggerInvoiceBatchDraftToPosted(String invoiceBatchRunId)`

#### Parameters

invoiceBatchRunId
:   Type: String
:   ID of the invoice batch run record that creates the draft invoices.

#### Return Value

Type: [`ConnectApi.InvoiceBatchDraftToPostedResult`](./apex_connectapi_output_invoice_batch_draft_to_posted_output.htm.md "Output representation of the batch update details of the invoices from Draft to Posted status.")

#### Usage

You need the Billing Operations User permission set to use this
method.

This method posts the draft invoices and changes the status of the invoices
from `Draft` to `Posted`.
