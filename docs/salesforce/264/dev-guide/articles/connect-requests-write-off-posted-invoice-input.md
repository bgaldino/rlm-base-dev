---
page_id: connect-requests-write-off-posted-invoice-input
title: Posted Invoice Write-Off Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-write-off-posted-invoice-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_write_off_posted_invoice_input.htm
fetched_at: 2026-11-25
---

# Posted Invoice Write-Off Input

Input representation of the details of the request to write off a posted invoice. This representation includes invoice details such as invoice ID and reason for writing off invoices.

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
| `invoiceId` | String | ID of the invoice record that you want to write off. | Required | 64.0 |
| `reason` | String | Reason for writing off invoices. | Optional | 64.0 |
| `reason​Code` | String | Code that categorizes the write-off reason. For example, if the reason for the invoice write-off is a disputed amount, the reason code can be Disputed Amount (DA). | Required | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-write-off-posted-invoice-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
