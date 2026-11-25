---
page_id: connect-responses-send-email-for-invoice-batch-run-output
title: Send Email Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-send-email-for-invoice-batch-run-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_send_email_for_invoice_batch_run_output.htm
fetched_at: 2026-11-25
---

# Send Email Response

Output representation of the API request to send emails for posted invoices.

## JSON Example

This example shows a sample response when the request is successful.

```
{
  "errors": [],
  "requestIdentifier": "5IRLT000001SIJB4A4",
  "success": true
}
```

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
| `errors` | [Send Email Error](./connect-responses-send-email-for-invoice-batch-run-error.md)[] | List of errors that occurred while trying to enqueue the request. In case of errors while sending emails, you can check the Revenue Transaction Error Logs of the InvoiceBatchRun record and associated Invoice record. An error occurs for these scenarios. The contact email or user isn’t configured; The configured email template isn’t valid; or Email is sent through a contact email, and the contact doesn’t have an associated user. In this scenario, the emails are counted against the general email limits. An error is thrown if you exceed the email limits. | Big, 65.0 | 65.0 |
| `requestIdentifier` | String | Unique identifier for the request, which corresponds to the invoice batch run ID. | Big, 65.0 | 65.0 |
| `success` | Boolean | Indicates whether the request to start the email sending process was successfully enqueued (`true`) or not (`false`). | Big, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-send-email-for-invoice-batch-run-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
