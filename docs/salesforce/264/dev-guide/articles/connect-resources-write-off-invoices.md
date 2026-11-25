---
page_id: connect-resources-write-off-invoices
title: Posted Invoice List Write-Off (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-write-off-invoices.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_write_off_invoices.htm
fetched_at: 2026-11-25
---

# Posted Invoice List Write-Off (POST)

Create credit memos with the total charge amount on the invoice as the write-off amount and close the invoice.

You can write off invoices to maintain accurate financial records and to prioritize invoices with a higher probability of payment, which is essential for compliance with accounting standards.

## Special Access Rules

To use this API, you need the Billing Operations User or Credit Memo Operations User permission set.

## Resource

```
/commerce/invoicing/invoices/actions/write-off
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/actions/write-off
```

## Available Version

64.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "invoices": [
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Bad Debt",
      "description": "Bad Debt"
    },
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Concession",
      "description": "Concession"
    }
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoices` | [Posted Invoice Write-Off Input](./connect-requests-write-off-posted-invoice-input.md)[] | Details of the invoices that you want to write off. | Required | 64.0 |

## Response Body for POST

[Posted Invoice List Write-Off](./connect-responses-write-off-posted-invoice-list-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-write-off-invoices.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
