---
page_id: connect_resources_calculate_estimated_tax.htm
title: Invoice Estimated Tax Calculation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_calculate_estimated_tax.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Invoice Estimated Tax Calculation (POST)

Calculate estimated tax for invoices with invoice lines that have the
`TaxProcessingStatus` as either `Pending` or `Estimated`.

Resource
:   ```
    /commerce/invoicing/invoices/collection/actions/calculate-estimated-tax
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/collection/actions/calculate-estimated-tax
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "invoiceIds": ["3ttxx0000004CIjAAM"]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `correlationId` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 63.0 |
        | `invoiceIds` | String[] | IDs of the invoices for which the estimated tax must be calculated. You can specify one invoice per API request. | Required | 63.0 |

Response body for POST
:   [Revenue Async Response](./connect_responses_revenue_async_output.htm.md "Output representation of the result of the API request with the request identifier.")
