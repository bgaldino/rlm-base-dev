---
page_id: connect-requests-standalone-credit-memo-tax-input
title: Standalone Credit Memo Tax Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-standalone-credit-memo-tax-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_standalone_credit_memo_tax_input.htm
fetched_at: 2026-11-25
---

# Standalone Credit Memo Tax Input

Input representation of the details of the tax request.

## JSON Example

```
[
  {
    "taxAmount": 200,
    "taxName": "Federal Tax",
    "taxRate": 1
  },
  {
    "taxAmount": 500,
    "taxName": "State Tax",
    "taxRate": 1
  }
]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `taxAmount` | Double | Amount of tax to be applied. | Required | 62.0 |
| `taxCode` | String | Tax code to be used to create the tax line. | Optional | 62.0 |
| `taxName` | String | Name of tax to be applied. | Optional | 62.0 |
| `taxRate` | Double | Tax rate to be used to create the tax line. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-standalone-credit-memo-tax-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
