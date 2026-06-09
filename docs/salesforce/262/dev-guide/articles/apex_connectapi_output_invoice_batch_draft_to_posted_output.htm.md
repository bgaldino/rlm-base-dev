---
page_id: apex_connectapi_output_invoice_batch_draft_to_posted_output.htm
title: ConnectApi.InvoiceBatchDraftToPostedResult
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_invoice_batch_draft_to_posted_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.InvoiceBatchDraftToPostedResult

Output representation of the batch update details of the invoices from `Draft` to `Posted`
status.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `invoiceBatchDraftToPostedId` | String | ID of the invoice batch draft to posted run record that’s created to track the batch process of posting the draft invoices that are associated with the parent invoice batch run record. | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | 62.0 |
