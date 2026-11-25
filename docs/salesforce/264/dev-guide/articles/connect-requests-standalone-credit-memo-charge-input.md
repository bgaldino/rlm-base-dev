---
page_id: connect-requests-standalone-credit-memo-charge-input
title: Standalone Credit Memo Charge Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-standalone-credit-memo-charge-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_standalone_credit_memo_charge_input.htm
fetched_at: 2026-11-25
---

# Standalone Credit Memo Charge Input

Input representation of the details of the charge lines of a credit memo.

## JSON Example

```
  "charges": [
    {
      "chargeAmount": 100,
      "productId": "01tR0000000njDiIAI"
    }
  ]
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Credit Memo Addresses Input](./connect-requests-credit-memo-addresses-input.md) | Details of the billing and shipping addresses. | Optional | 62.0 |
| `charge​Amount` | Double | Charge amount for the credit memo. | Required | 62.0 |
| `custom​Fields` | Map | Custom field values on each credit memo line in the charges list, as key-value pairs. | Optional | 68.0 |
| `description` | String | Description of the created credit memo charge line. | Optional | 62.0 |
| `endDate` | String | End date of the credit memo charge line. | Optional | 62.0 |
| `isTax​OnlyCredit` | Boolean | Indicates whether the credit is for tax only (`true`) or not (`false`). | Optional | 62.0 |
| `product​Id` | String | ID of the product record that the credit memo is issued on. | Optional | 62.0 |
| `product​Name` | String | Name of the product that the credit memo is issued on. | Optional | 62.0 |
| `startDate` | String | Start date of the credit memo charge line. | Optional | 62.0 |
| `taxEffective​Date` | String | Date from when the tax is applicable. | Optional | 62.0 |
| `taxes` | [Standalone Credit Memo Tax Input](./connect-requests-standalone-credit-memo-tax-input.md)[] | List of credit memo tax lines. | Optional | 62.0 |
| `taxStrategy` | String | Tax strategy to be applied to this credit memo charge line, child treatment lines, and tax lines. You can override the tax strategy at the individual credit memo lines or tax lines level. | Optional | 62.0 |
| `treatment​Id` | String | ID of the tax treatment record that’s used to calculate tax. | Optional | 62.0 |

Valid values are:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `Manual Override`—Specifies that the provided tax values must be considered for taxes.

- `Calculate`—Specifies that tax must be calculated by using the API.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-standalone-credit-memo-charge-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
