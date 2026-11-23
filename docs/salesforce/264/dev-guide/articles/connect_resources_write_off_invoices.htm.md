---
page_id: connect_resources_write_off_invoices.htm
title: Posted Invoice List Write-Off (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_write_off_invoices.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
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
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/invoices/actions/write-off
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
| `invoices` | [Posted Invoice Write-Off Input](./connect_requests_write_off_posted_invoice_input.htm.md "Input representation of the details of the request to write off a posted invoice. This representation includes invoice details such as invoice ID and reason for writing off invoices.")[] | Details of the invoices that you want to write off. | Required | 64.0 |

## Response Body for POST

[Posted Invoice List Write-Off](./connect_responses_write_off_posted_invoice_list_output.htm.md "Output representation of the list of invoices that are written off.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_write_off_invoices.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
