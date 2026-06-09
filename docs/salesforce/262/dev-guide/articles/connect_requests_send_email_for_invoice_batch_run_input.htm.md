---
page_id: connect_requests_send_email_for_invoice_batch_run_input.htm
title: Send Email Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_send_email_for_invoice_batch_run_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Send Email Input

Input representation of the request to send an email for an invoice batch
run.

JSON example
:   ```
    {
      "invoiceBatchRunId": "5IRLT000001SIJB4A4"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `invoiceBatchRunId` | String | ID of the invoice batch run record to send emails for the posted invoices of an invoice batch run. | Required | 65.0 |
