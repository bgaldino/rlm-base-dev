---
page_id: connect-responses-send-email-for-invoice-batch-run-error
title: Send Email Error
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-send-email-for-invoice-batch-run-error.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_send_email_for_invoice_batch_run_error.htm
fetched_at: 2026-11-25
---

# Send Email Error

Output representation of the error response of the API request to send emails for posted invoices.

## JSON Example

This example shows a sample response with an error scenario.

```
{
  "errors": [
    {
      "errorCode": "INVALID_API_INPUT",
      "errorMessage": "Specify a valid invoiceBatchRunId."
    }
  ],
  "requestIdentifier": "5IRxx0000004CKKGA2",
  "success": false
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Unique code for the error. | Big, 65.0 | 65.0 |
| `errorMessage` | String | Descriptive message for the error. | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-send-email-for-invoice-batch-run-error.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
