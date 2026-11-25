---
page_id: connect-resources-create-ramp-deal
title: Create Ramp Deal (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-ramp-deal.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_create_ramp_deal.htm
fetched_at: 2026-11-25
---

# Create Ramp Deal (POST)

Create a ramp deal for a customer on a product. Sales reps can use ramp deals to provide yearly deals to a customer, resulting in long-term revenue and customer relationship. A customer can create, update, or view multiple segments of periods for their subscription term with different attributes for each segment.

This API request creates segments based on the specified input properties such as term, segment type, and trial details. The API response includes the context ID and the updated context object for the sales transaction. You must call the Place Sales Transaction API by specifying this context ID to apply the ramp deal updates. See [Place Sales Transaction API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_place_sales_transaction.htm) .

**Note:**

This API is applicable when you’re working with line ramps. To work with ramp deals for groups, you must use the Place Sales Transaction API and specify the `groupRampActions` property.

## Resource

```
/connect/revenue-management/sales-transaction-contexts/{resourceId}/actions/ramp-deal-create
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/{0QLxx0000004CfIGAU}/actions/ramp-deal-create
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `resourceId` | String | ID of the quote line item, order item, or context. | Required | 62.0 |

## Request Body for POST

**JSON Example**

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

**Properties**

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

## Response Body for POST

[Ramp Deal Service](./connect-responses-ramp-deal-service-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-ramp-deal.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
