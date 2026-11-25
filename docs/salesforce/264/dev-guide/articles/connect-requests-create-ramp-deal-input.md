---
page_id: connect-requests-create-ramp-deal-input
title: Create Ramp Deal Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-create-ramp-deal-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_create_ramp_deal_input.htm
fetched_at: 2026-11-25
---

# Create Ramp Deal Input

Input representation of the request to create a ramp deal.

## JSON Example

```
{
  "transactionId": "0Q0xx0000004C92CAE",
  "transactionLineId": "0QLxx0000004C9VGAU",
  "subscriptionTerm": 14,
  "subscriptionTermUnit": "MONTHS",
  "trialTerm": 45,
  "trialTermUnit": "DAYS",
  "segmentType": "YEARLY",
  "executionSettings": {
       "executePricing": true,
       "executeConfigRules": false
   }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `execution​Settings` | [Execution Settings Input](./connect-requests-execution-settings-input.md)[] | Settings to run the pricing or configuration rules. | Optional | 62.0 |
| `segment​Type` | String | Type of segment that the user wants to create. Valid values are `FREE_TRIAL`, `CUSTOM`, or `YEARLY`. | Required | 62.0 |
| `subscription​Term` | Integer | Subscription length of the term-defined product. | Required | 62.0 |
| `subscription​TermUnit` | String | Unit of time for the subscription length. Valid value is `MONTHS`. | Required | 62.0 |
| `transaction​Id` | String | ID of the sales transaction that’s configured, such as quote or order. | Required | 62.0 |
| `transaction​LineId` | String | Quote line item ID or order item ID that the price ramp is created for. | Required | 62.0 |
| `trialTerm` | Integer | Length of the trial period, if any. | Optional | 62.0 |
| `trialTerm​Unit` | String | Unit of time for the trial period. Valid value is `DAYS`. | Optional. Required if `trialTerm` property is specified. | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-create-ramp-deal-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
