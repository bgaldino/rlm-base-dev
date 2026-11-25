---
page_id: apex-connectapi-input-standalone-credit-memo-charge
title: ConnectApi.StandaloneCreditMemoChargeInputRequest
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-standalone-credit-memo-charge.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-apex-input-classes
legacy_page_id: apex_connectapi_input_standalone_credit_memo_charge.htm
fetched_at: 2026-11-25
---

# ConnectApi.StandaloneCreditMemoChargeInputRequest

Input representation of the details of the charge lines of a credit memo.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addresses` | [Credit Memo Addresses Input](./apex-connectapi-input-credit-memo-addresses.md) | Details of the billing and shipping addresses. | Optional | 62.0 |
| `chargeAmount` | Double | Charge amount for the credit memo. | Required | 62.0 |
| `description` | String | Description of the created credit memo charge line. | Optional | 62.0 |
| `endDate` | String | End date of the credit memo charge line. | Optional | 62.0 |
| `isTaxOnlyCredit` | Boolean | Indicates whether the credit is for tax only (`true`) or not (`false`). | Optional | 62.0 |
| `productId` | String | ID of the product record that the credit memo is issued on. | Optional | 62.0 |
| `productName` | String | Name of the product that the credit memo is issued on. | Optional | 62.0 |
| `startDate` | String | Start date of the credit memo charge line. | Optional | 62.0 |
| `taxEffectiveDate` | String | Date from when the tax is applicable. | Optional | 62.0 |
| `taxes` | List[ConnectApi.StandaloneCreditMemoTaxInputRequest](./apex-connectapi-input-standalone-credit-memo-tax.md) | List of credit memo tax lines. | Optional | 62.0 |
| `taxStrategy` | `ConnectApi.StandaloneTaxStrategyEnum` | Tax strategy to be applied to this credit memo charge line, child treatment lines, and tax lines. You can override the tax strategy at the individual credit memo lines or tax lines level. | Optional | 62.0 |
| `treatmentId` | String | ID of the tax treatment record that’s used to calculate tax. | Optional | 62.0 |

taxStrategy values:

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `Manual Override`—Specifies that the provided tax values must be considered for taxes.

- `Calculate`—Specifies that tax must be calculated by using the API.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/apex-connectapi-input-standalone-credit-memo-charge.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
