---
page_id: connect-requests-convert-negative-invoice-lines-input
title: Convert Negative Invoice Lines Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-convert-negative-invoice-lines-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_convert_negative_invoice_lines_input.htm
fetched_at: 2026-11-25
---

# Convert Negative Invoice Lines Input

Input representation of the details of the request to convert a list of negative invoice lines into a credit.

## JSON Example

```
  {
  "invoiceLines": ["5TVxx0000004C92GAE", "5TVxx0000004C93GAE"],
  "description": "Convert negative invoice lines into credit",
  "effectiveDate":"2022-05-18"
  }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description stamped on the credit memo that’s created after the negative invoice line conversion. | Optional | 62.0 |
| `effectiveDate` | String | Date stamped on the credit memo that’s created after the negative invoice line conversion. | Required | 62.0 |
| `invoiceLines` | String[] | Complete list of the negative invoice lines along with the associated invoice line taxes. The specified negative invoice lines are converted into a posted credit memo. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-convert-negative-invoice-lines-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
