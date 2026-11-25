---
page_id: connect-requests-invoice-preview-input
title: Invoice Preview Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-invoice-preview-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_invoice_preview_input.htm
fetched_at: 2026-11-25
---

# Invoice Preview Input

Input representation of the details of the billing transaction that the preview invoices are generated for.

## JSON Example

```
{
    "billingTransactionId": "801Z600000004LoIAI",
    "numberOfBillingPeriods": 2,
    "previewDate": "2024-12-04"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​TransactionId` | String | ID of the record to generate the preview invoices for. | Required | 63.0 |
| `numberOf​BillingPeriods` | Integer | Number of billing periods that the invoice preview is generated for. If unspecified, the default value is `2`. | Optional | 64.0 |
| `preview​Date` | String | The date on which the preview invoice is generated. For the first invoice, the preview date is the target date for generating the invoice. For the second invoice, the target date is calculated based on the preview date and the minimum billing frequency of the transactions. The default value is the current date. | Optional | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-invoice-preview-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
