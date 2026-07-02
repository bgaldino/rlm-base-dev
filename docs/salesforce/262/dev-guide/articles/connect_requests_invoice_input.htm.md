---
page_id: connect_requests_invoice_input.htm
title: Invoice Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Invoice Input

Input representation of the details of the billing
schedule.

JSON example
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
