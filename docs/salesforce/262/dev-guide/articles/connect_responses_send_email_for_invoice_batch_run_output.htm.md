---
page_id: connect_responses_send_email_for_invoice_batch_run_output.htm
title: Send Email Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_send_email_for_invoice_batch_run_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Send Email Response

Output representation of the API request to send emails for posted
invoices.

JSON example
:   This example shows a sample response when the request is
    successful.

    ```
    {
      "errors": [],
      "requestIdentifier": "5IRLT000001SIJB4A4",
      "success": true
    }
    ```
:   This example shows a sample response with an error
    scenario.

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
| `errors` | [Send Email Error](./connect_responses_send_email_for_invoice_batch_run_error.htm.md "Output representation of the error response of the API request to send emails for posted invoices.")[] | List of errors that occurred while trying to enqueue the request. In case of errors while sending emails, you can check the Revenue Transaction Error Logs of the InvoiceBatchRun record and associated Invoice record.  An error occurs for these scenarios.   - The contact email or user isn't configured. - The configured email template isn't valid. - Email is sent through a contact email, and the contact doesn't have an   associated user. In this scenario, the emails are counted against the general   email limits. An error is thrown if you exceed the email limits. | Big, 65.0 | 65.0 |
| `requestIdentifier` | String | Unique identifier for the request, which corresponds to the invoice batch run ID. | Big, 65.0 | 65.0 |
| `success` | Boolean | Indicates whether the request to start the email sending process was successfully enqueued (`true`) or not (`false`). | Big, 65.0 | 65.0 |
