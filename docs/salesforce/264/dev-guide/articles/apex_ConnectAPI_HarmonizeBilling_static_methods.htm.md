---
page_id: apex_ConnectAPI_HarmonizeBilling_static_methods.htm
title: HarmonizeBilling Class
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_ConnectAPI_HarmonizeBilling_static_methods.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_connect_api_namespace.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

 

# HarmonizeBilling Class

 
 
 
Update the status of the invoice from Draft to Posted by using the HarmonizeBilling
  class.

  

## Namespace

   
   

ConnectApi

  

 

 

## HarmonizeBilling Methods

 These methods are for `HarmonizeBilling`. All
  methods are static.

 

- 
**[postDraftInvoices(inputRequest)](./apex_ConnectAPI_HarmonizeBilling_static_methods.htm.md#apex_ConnectAPI_HarmonizeBilling_postDraftInvoices_1)**  

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

: Type: [`ConnectApi.InvoiceDraftToPostedInputRequest`](./apex_connectapi_input_invoice_draft_to_posted.htm.md)

: Input representation of the details of the draft invoice that’s posted.

#### Return Value

Type: [`ConnectApi.RevenueAsyncRepresentation`](./apex_connectapi_output_revenue_async.htm.md)

#### Usage

You need the Billing Operations User permission set to use this
        method.

This method calls an external tax engine to calculate taxes for the draft
        invoice, posts the invoice, and updates the related billing schedules and billing
        periods.
