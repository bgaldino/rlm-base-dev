---
page_id: apex_ConnectAPI_HarmonizeBilling_static_methods.htm
title: HarmonizeBilling Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_HarmonizeBilling_static_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-11-23
---

# HarmonizeBilling Class

Update the status of the invoice from Draft to Posted by using the HarmonizeBilling
class.

## Namespace

[ConnectApi](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_classes_connect_api.htm "HTML (New Window)")

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

**inputRequest**

Type: [`ConnectApi.InvoiceDraftToPostedInputRequest`](./apex_connectapi_input_invoice_draft_to_posted.htm.md "Input representation of the details of the draft invoice that’s posted.")

Input representation of the details of the draft invoice that’s posted.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex_connectapi_output_revenue_async.htm.md "Output representation of the result of the API request with the request identifier.")

#### Usage

You need the Billing Operations User permission set to use this method.

This method calls an external tax engine to calculate taxes for the draft invoice, posts the invoice, and updates the related billing schedules and billing periods.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_HarmonizeBilling_static_methods.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
