---
page_id: connect_responses_invoice_batch_draft_to_posted_output.htm
title: Invoice Batch Draft To Posted
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_batch_draft_to_posted_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Invoice Batch Draft To Posted

Output representation of the batch update details of the invoices from `Draft` to `Posted`
status.

JSON example
:   ```
    {
      "invoiceBatchDraftToPostedId": "4sFDU00000000652AA",
      "success": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatch​DraftToPostedId` | String | ID of the invoice batch draft to posted run record that’s created to track the batch process of posting the draft invoices that are associated with the parent invoice batch run record. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
