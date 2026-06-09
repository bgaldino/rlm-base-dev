---
page_id: connect_responses_tax_engine_log_output.htm
title: Tax Engine Log
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_engine_log_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Tax Engine Log

Output representation of the logs that the tax engine generates.

JSON example
:   ```
    {
      "taxEngineLogs": [
        {
          "createdDate": "2022-03-09T10:55:38.000Z",
          "id": "3l1xx00000000PpAAI",
          "resultCode": "Success"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `createdDate` | String | Date when the tax engine creates the log. | Big, 62.0 | 62.0 |
| `id` | String | ID of the tax engine log record. | Big, 62.0 | 62.0 |
| `resultCode` | String | Result code associated with the created log. | Big, 62.0 | 62.0 |
