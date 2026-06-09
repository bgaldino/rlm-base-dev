---
page_id: apex_ConnectAPI_HarmonizeBilling_static_methods.htm
title: HarmonizeBilling Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_HarmonizeBilling_static_methods.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-06-09
---

# HarmonizeBilling Class

Update the status of the invoice from Draft to Posted by using the HarmonizeBilling
class.

## Namespace

ConnectApi

## HarmonizeBilling Methods

These methods are for `HarmonizeBilling`. All
methods are static.

- **[postDraftInvoices(inputRequest)](./apex_ConnectAPI_HarmonizeBilling_static_methods.htm.md#apex_ConnectAPI_HarmonizeBilling_postDraftInvoices_1)**  
  Update the status of the invoice from Draft to Posted.

### postDraftInvoices(inputRequest)

Update the status of the invoice from Draft to Posted.

#### API Version

62.0

#### Requires Chatter

No

#### Signature

`public static ConnectApi.RevenueAsyncRepresentation postDraftInvoices(ConnectApi.InvoiceDraftToPostedInputRequest inputRequest)`

#### Parameters

inputRequest
:   Type: [`ConnectApi.InvoiceDraftToPostedInputRequest`](./apex_connectapi_input_invoice_draft_to_posted.htm.md "Input representation of the details of the draft invoice that’s posted.")
:   Input representation of the details of the draft invoice that’s posted.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex_connectapi_output_revenue_async.htm.md "Output representation of the result of the API request with the request identifier.")

#### Usage

You need the Billing Operations User permission set to use this
method.

This method calls an external tax engine to calculate taxes for the draft
invoice, posts the invoice, and updates the related billing schedules and billing
periods.
