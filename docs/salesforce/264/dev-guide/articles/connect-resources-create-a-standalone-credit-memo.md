---
page_id: connect-resources-create-a-standalone-credit-memo
title: Standalone Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-a-standalone-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_create_a_standalone_credit_memo.htm
fetched_at: 2026-11-25
---

# Standalone Credit Memo (POST)

Create a credit memo without applying it to an invoice. You can credit the invoice at a later date.

In the API request, specify the credit memo header information, charge parameters, adjustment parameters, and tax parameters. A credit memo requires at least one credit memo line. The credit memo line can be a charge or an adjustment.

Specify the credit memo lines that you want as lists of charges and adjustments. Each credit memo line must be related to a product.

## Special Access Rules

You need the Credit Memo Operations User permission set to use this API.

## Resource

```
/commerce/invoicing/credit-memos/actions/generate
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/credit-memos/actions/generate
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billTo​ContactId` | String | Contact related to the credit memo. | Optional | 62.0 |
| `billing​AccountId` | String | ID of the account that the credit is issued to. | Required | 62.0 |
| `charges` | [Standalone Credit Memo Charge Input](./connect-requests-standalone-credit-memo-charge-input.md)[] | Charge lines of the credit memo. Requires at least one charge line. | Required | 62.0 |
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

- `Ignore`—Specifies that the creation of tax lines must be ignored.

- `Manual Override`—Specifies that the provided tax values must be considered for taxes.

- `Calculate`—Specifies that tax must be calculated by using the API.

## Response Body for POST

[Revenue Async Response](./connect-responses-revenue-async-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-a-standalone-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
