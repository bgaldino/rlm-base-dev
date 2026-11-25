---
page_id: connect-requests-write-off-posted-invoice-list-input
title: Posted Invoice List Write-Off Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-write-off-posted-invoice-list-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_write_off_posted_invoice_list_input.htm
fetched_at: 2026-11-25
---

# Posted Invoice List Write-Off Input

Input representation of the request to write off a list of posted invoices. This representation includes the details of invoices that you want to write off.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoices` | [Posted Invoice Write-Off Input](./connect-requests-write-off-posted-invoice-input.md)[] | Details of the invoices that you want to write off. | Required | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-write-off-posted-invoice-list-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
