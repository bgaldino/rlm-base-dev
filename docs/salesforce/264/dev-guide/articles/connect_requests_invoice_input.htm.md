---
page_id: connect_requests_invoice_input.htm
title: Invoice Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Invoice Input

Input representation of the details of the billing schedule.

## JSON Example

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

## Properties

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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_invoice_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
