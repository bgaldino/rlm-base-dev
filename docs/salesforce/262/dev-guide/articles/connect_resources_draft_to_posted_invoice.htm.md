---
page_id: connect_resources_draft_to_posted_invoice.htm
title: Invoice Draft to Posted Status (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_draft_to_posted_invoice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Invoice Draft to Posted Status (POST)

Update the status of the invoice from Draft to
Posted.

This API calls an external tax engine or provides information to your tax adapter implementation
to calculate taxes for the draft invoice, post the invoice, and update the related billing
schedules and billing periods.

Special Access Rules
:   You need the Billing Operations User permission set to use this API.

Resource
:   ```
    /commerce/invoicing/invoices/collection/actions/post
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/collection/actions/post
    ```

Available version
:   62.0

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
        | `correlationId` | String | Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). | Optional | 62.0 |
        | `invoiceIds` | String[] | IDs of the invoice records in `Draft` status to be posted. You can post one draft invoice per API request. | Required | 62.0 |

Response body for POST
:   [Revenue Async Response](./connect_responses_revenue_async_output.htm.md "Output representation of the result of the API request with the request identifier.")
