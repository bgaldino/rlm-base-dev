---
page_id: connect_resources_delete_ramp_deal.htm
title: Delete Ramp Deal (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_delete_ramp_deal.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-11-23
---

# Delete Ramp Deal (POST)

Delete a ramp deal to convert a ramped product to include a single quote line item or order item.

This API request deletes the segments related to the product. The API response
includes the updated context with the context ID. You must call the Place Sales Transaction
(POST) API by specifying this context ID to apply the ramp deal updates. See [Place Sales Transaction (POST)
API](./connect_resources_place_sales_transaction.htm.md "HTML (New Window)").

This API is applicable when you're working with line ramps. To work
with ramp deals for groups, you must use the Place Sales Transaction API and specify the
`groupRampActions` property.

## Resource

```
/connect/revenue-management/sales-transaction-contexts/resourceId/actions/ramp-deal-delete
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/revenue-management/sales-transaction-contexts/0QLxx0000004CfIGAU/actions/ramp-deal-delete
```

## Available Version

62.0

## HTTP Methods

POST

## Path Parameter for POST

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `resourceId` | String | ID of the context. | Required | 62.0 |

## Request Body for POST

**JSON Example**

```
{
  "rampDealIds": [
    "0Q0xx0000004CDxCAM",
    "0QLxx0000004CSOGA2"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rampDeal​Ids` | String[] | Ramp identifier on the quote line item or order item. | Required | 62.0 |

## Response Body for POST

[Ramp Deal Service](./connect_responses_ramp_deal_service_output.htm.md "Output representation of the details of a created, updated, or deleted ramp deal.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_delete_ramp_deal.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
