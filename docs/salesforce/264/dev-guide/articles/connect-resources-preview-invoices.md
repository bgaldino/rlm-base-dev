---
page_id: connect-resources-preview-invoices
title: Invoice Preview (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-preview-invoices.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_preview_invoices.htm
fetched_at: 2026-11-25
---

# Invoice Preview (POST)

Generate preview invoices, which includes the estimated tax amounts, for a billing transaction for the next two billing periods.

Invoice preview provides details of the upcoming invoices for orders or quotes within the system.

## Special Access Rules

You need the Billing Operations User or Billing Customer Service permission set to use this API.

See these [requirements](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_procedure_plan_create.htm) to learn more about the configuration prerequisites.

## Resource

```
/commerce/invoicing/invoices/collection/actions/preview
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/collection/actions/preview
```

## Available Version

63.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "billingTransactionId": "801Z600000004LoIAI",
    "numberOfBillingPeriods": 2,
    "previewDate": "2024-12-04"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​TransactionId` | String | ID of the record to generate the preview invoices for. | Required | 63.0 |
| `numberOf​BillingPeriods` | Integer | Number of billing periods that the invoice preview is generated for. If unspecified, the default value is `2`. | Optional | 64.0 |
| `preview​Date` | String | The date on which the preview invoice is generated. For the first invoice, the preview date is the target date for generating the invoice. For the second invoice, the target date is calculated based on the preview date and the minimum billing frequency of the transactions. The default value is the current date. | Optional | 63.0 |

## Response Body for POST

[Invoice Preview](./connect-responses-invoice-preview-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-preview-invoices.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
