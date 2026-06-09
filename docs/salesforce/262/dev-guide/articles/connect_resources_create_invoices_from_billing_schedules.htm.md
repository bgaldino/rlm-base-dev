---
page_id: connect_resources_create_invoices_from_billing_schedules.htm
title: Invoice Creation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_invoices_from_billing_schedules.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Invoice Creation (POST)

Create an invoice for an account, order, or a list of billing
schedules.

This API request creates billing period items for the matching billing schedules.
The billing period items are created for the period between the next charge date of the
billing schedule and the specified target date. Invoice lines are created by processing
these billing period items. These invoice lines are then grouped into invoices based on the
defined grouping criteria on the billing schedule.

This API also applies any available
credits on an account to settle an invoice and to reduce it's balance. To apply available
credits, ensure the **Apply Credits to Posted Invoices** setting from
Billing Settings is turned on.

Special Access Rules
:   You need the Generate Invoices From Billing Schedule API, Billing Operations User, or Billing
    Customer Service permission set to use this API.

Resource
:   ```
    /commerce/invoicing/invoices/collection/actions/generate
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/collection/actions/generate
    ```

Available version
:   62.0

HTTP methods
:   POST

Request body for POST
:   ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=revenue_lifecycle_management_dev_guide)

    #### Note

    The `billing​TransactionId` property
    takes precedence over the `accountId` property followed by
    the `billing​ScheduleIds` property when
    values for these properties are specified in the input request.
:   JSON example
    :   ```
        {
          "accountId": "001SG00000mYtRWYA0",
          "action": "Posted",
          "billingScheduleIds": [
            "44bSG000000CVeMYAW"
          ],
          "billingTransactionId": "801SG00000mYtaXYAS",
          "correlationId": null,
          "invoiceDate": "2024-01-12",
          "targetDate": "2024-01-12"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `accountId` | String | ID of the account record to create the invoices for. | Required if the `billing​ScheduleIds` or `billing​TransactionId` property isn’t specified. | 63.0 |
        | `action` | String | Type of invoice to be created. Valid values are:   - `Draft` - `Posted` | Required | 62.0 |
        | `billing​ScheduleIds` | String[] | List of billing schedule IDs that’s used to create the invoices. You can specify a maximum of 200 billing schedules. | Required if the `accountId` or `billing​TransactionId` property isn’t specified. | 62.0 |
        | `billing​TransactionId` | String | ID of the billing transaction record, which is the order ID, to create the invoices for. | Required if the `accountId` or `billing​ScheduleIds` property isn’t specified. | 63.0 |
        | `correlation​Id` | String | Property that’s tagged against the published `InvoiceProcessedEvent` event, if specified. | Optional | 62.0 |
        | `invoice​Date` | String | Stamping date of the invoice in ISO 8601 format. | Required | 62.0 |
        | `target​Date` | String | Date in ISO 8601 format used to decide the billing periods that are included to create invoices. | Required | 62.0 |

Response body for POST
:   [Revenue Async
    Response](./connect_responses_revenue_async_output.htm.md "Output representation of the result of the API request with the request identifier.")
