---
page_id: connect-requests-credit-invoice-line-tax-input
title: Credit Invoice Line Tax Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-invoice-line-tax-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_credit_invoice_line_tax_input.htm
fetched_at: 2026-11-25
---

# Credit Invoice Line Tax Input

Input representation of the details of the tax lines to be created manually for the invoice line.

## JSON Example

```
      "taxes": [
        {
          "taxAmount": 15,
          "taxName": "abc",
          "taxCode": "taxCode",
          "taxRate": 7
        }
      ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `taxAmount` | Double | Amount of tax to be applied related to this invoice line. | Required | 62.0 |
| `taxCode` | String | Tax code to be applied related to this invoice line to create the tax line. | Optional | 62.0 |
| `taxName` | String | Name of tax to be applied related to this invoice line. | Optional | 62.0 |
| `taxRate` | Double | Tax rate used to create the tax line. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-credit-invoice-line-tax-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
