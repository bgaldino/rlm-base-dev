---
page_id: connect_responses_invoice_batch_draft_to_posted_output.htm
title: Invoice Batch Draft To Posted
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_batch_draft_to_posted_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Invoice Batch Draft To Posted

Output representation of the batch update details of the invoices from `Draft` to `Posted` status.

## JSON Example

```
{
  "invoiceBatchDraftToPostedId": "4sFDU00000000652AA",
  "success": true
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceBatch​DraftToPostedId` | String | ID of the invoice batch draft to posted run record that’s created to track the batch process of posting the draft invoices that are associated with the parent invoice batch run record. | Small, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoice_batch_draft_to_posted_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
