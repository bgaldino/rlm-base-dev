---
page_id: connect_responses_send_email_for_invoice_batch_run_error.htm
title: Send Email Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_send_email_for_invoice_batch_run_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Send Email Error

Output representation of the error response of the API request to send emails for
posted invoices.

JSON example
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
| `errorCode` | String | Unique code for the error. | Big, 65.0 | 65.0 |
| `errorMessage` | String | Descriptive message for the error. | Big, 65.0 | 65.0 |
