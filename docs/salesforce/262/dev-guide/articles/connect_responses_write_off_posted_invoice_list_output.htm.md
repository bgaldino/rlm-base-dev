---
page_id: connect_responses_write_off_posted_invoice_list_output.htm
title: Posted Invoice List Write-Off
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_write_off_posted_invoice_list_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Posted Invoice List Write-Off

Output representation of the list of invoices that are written off.

JSON example
:   ```
    {
      "result": [
        {
          "requestIdentifier": null,
          "invoiceId": "3t00000000CwAGI",
          "success": false,
          "errors": {
            "errorcode": "INVALID_API_INPUT",
            "errorMessage": "Reason is missing."
          }
        },
        {
          "requestIdentifier": 37612787,
          "invoiceId": "3t00000000CwAAI",
          "success": true,
          "errors": {
            "errorcode": null,
            "errorMessage": null
          }
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `result` | [Posted Invoice Write-Off](./connect_responses_write_off_posted_invoice_output.htm.md "Output representation of the details of a posted invoice that's written off.") [] | Details of the invoices for which the write-off process is initiated. | Big, 64.0 | 64.0 |
