---
page_id: connect_resources_create_invoices_from_billing_schedules.htm
title: Invoice Creation (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_invoices_from_billing_schedules.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Invoice Creation (POST)

Create an invoice for an account, order, or a list of billing schedules.

This API request creates billing period items for the matching billing schedules. The billing period items are created for the period between the next charge date of the billing schedule and the specified target date. Invoice lines are created by processing these billing period items. These invoice lines are then grouped into invoices based on the defined grouping criteria on the billing schedule.

This API also applies any available credits on an account to settle an invoice and to reduce it's balance. To apply available credits, ensure the **Apply Credits to Posted Invoices** setting from Billing Settings is turned on.

## Special Access Rules

You need the Generate Invoices From Billing Schedule API, Billing Operations User, or Billing Customer Service permission set to use this API.

## Resource

```
/commerce/invoicing/invoices/collection/actions/generate
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/collection/actions/generate
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**Note:** The `billing​TransactionId` property takes precedence over the `accountId` property followed by the `billing​ScheduleIds` property when values for these properties are specified in the input request.

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account record to create the invoices for. | Required if the `billing​ScheduleIds` or `billing​TransactionId` property isn’t specified. | 63.0 |
| `action` | String |  | Required | 62.0 |
| `billing​ScheduleIds` | String[] | List of billing schedule IDs that’s used to create the invoices. You can specify a maximum of 200 billing schedules. | Required if the `accountId` or `billing​TransactionId` property isn’t specified. | 62.0 |
| `billing​TransactionId` | String | ID of the billing transaction record, which is the order ID, to create the invoices for. | Required if the `accountId` or `billing​ScheduleIds` property isn’t specified. | 63.0 |
| `correlation​Id` | String | Property that’s tagged against the published `InvoiceProcessedEvent` event, if specified. | Optional | 62.0 |
| `invoice​Date` | String | Stamping date of the invoice in ISO 8601 format. | Required | 62.0 |
| `target​Date` | String | Date in ISO 8601 format used to decide the billing periods that are included to create invoices. | Required | 62.0 |

Supported values:

- `Draft`
- `Posted`

## Response Body for POST

[Revenue Async Response](./connect_responses_revenue_async_output.htm.md "Output representation of the result of the API request with the request identifier.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_invoices_from_billing_schedules.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
