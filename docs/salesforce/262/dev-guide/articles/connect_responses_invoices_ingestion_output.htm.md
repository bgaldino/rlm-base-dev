---
page_id: connect_responses_invoices_ingestion_output.htm
title: Invoice Ingestion
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_invoices_ingestion_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Invoice Ingestion

Output representation of the details of the generated invoices.

JSON example
:   ```
    {
      "invoices": [
        {
          "errors": null,
          "invoiceId": "3ttxx0000000GRNAA2",
          "requestIdentifier": "16e80fbc-e7b3-4462-9439-745647fcf0a8",
          "statusURL": "/services/data/v63.0/sobjects/AsyncOperationTracker/16Pxx0000004Gz2EAE",
          "success": true
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `invoices` | [Invoice Ingestion](./connect_responses_invoice_ingestion_output.htm.md "Output representation of the details of a generated invoice.") [] | Result that contains the details for each generated invoice. | Big, 63.0 | 63.0 |
