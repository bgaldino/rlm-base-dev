---
page_id: connect_requests_standalone_credit_memo_tax_input.htm
title: Standalone Credit Memo Tax Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_standalone_credit_memo_tax_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_standalone_credit_memo_tax_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
