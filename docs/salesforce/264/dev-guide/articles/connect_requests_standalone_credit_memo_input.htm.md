---
page_id: connect_requests_standalone_credit_memo_input.htm
title: Standalone Credit Memo Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_standalone_credit_memo_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Standalone Credit Memo Input

Input representation of the details required to create a standalone credit memo.

## JSON Example

This example shows a sample request with the `Ignore` tax strategy.

```
{
  "billingAccountId": "001j000000WCFB800x",
  "type": "Posted",
  "description": "Standalone credit memo with ignored tax.",
  "currencyIsoCode": "USD",
  "taxStrategy": "Ignore",
  "charges": [
    {
      "chargeAmount": 100,
      "productId": "01tR0000000njDiIAI"
    }
  ]
}
```

This example shows a sample request with the `ManualOverride` tax strategy.

```
{
  "billingAccountId": "001DU000001nhoPYAQ",
  "description": "creditmemo-1",
  "currencyIsoCode": "USD",
  "taxStrategy": "ManualOverride",
  "charges": [
    {
      "productId": "01tDU000000EpKkYAK",
      "chargeAmount": 1000,
      "taxes": [
        {
          "taxAmount": 7.25,
          "taxCode": "CA-94121",
          "taxName": "CALIFORNIA",
          "taxRate": 0.25
        }
      ]
    }
  ]
}
```

This example shows a sample request with the `Calculate` tax strategy for a charge line.

```
{
  "billingAccountId": "001DU000001nhoPYAQ",
  "description": "Standalone Credit Memo",
  "type": "Posted",
  "currencyIsoCode": "USD",
  "taxStrategy": "Ignore",
  "charges": [
    {
      "productId": "01tR0000000njDiIAI",
      "chargeAmount": 10,
      "taxStrategy": "Calculate",
      "treatmentId": "1ttxx00000001VZAAY"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billTo​ContactId` | String | Contact related to the credit memo. | Optional | 62.0 |
| `billing​AccountId` | String | ID of the account that the credit is issued to. | Required | 62.0 |
| `charges` | [Standalone Credit Memo Charge Input](./connect_requests_standalone_credit_memo_charge_input.htm.md "Input representation of the details of the charge lines of a credit memo.")[] | Charge lines of the credit memo. Requires at least one charge line. | Required | 62.0 |
| `currency​IsoCode` | String | ISO code currency of the new credit that’s issued. | Optional | 62.0 |
| `custom​Fields` | Map | Custom field values on the credit memo record, as key-value pairs. | Optional | 68.0 |
| `description` | String | Description for the new credit that’s issued. | Optional | 62.0 |
| `effective​Date` | String | Effective date of the credit memo. If the value isn’t specified, then it’s null. | Optional | 62.0 |
| `external​Reference` | String | ID of the external reference for the credit memo. | Optional | 62.0 |
| `externalReference​Data​Source` | String | Source of the external reference for the credit memo. | Optional | 62.0 |
| `taxEffective​Date` | String | Effective date of the credit memo tax. If the value isn’t specified, then it’s null. | Optional | 62.0 |
| `tax​Strategy` | String | Specifies how tax lines must be created for the standalone credit memos. | Required | 62.0 |
| `type` | String |  | Optional | 62.0 |

Valid values are:

- `Ignore`—Specifies that the creation of tax
  lines must be ignored.
- `Manual Override`—Specifies that the provided
  tax values must be considered for taxes.
- `Calculate`—Specifies that tax must be
  calculated by using the API.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_standalone_credit_memo_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
