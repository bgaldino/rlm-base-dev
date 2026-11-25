---
page_id: connect-resources-rating-waterfall-fetch
title: Rating Waterfall (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-rating-waterfall-fetch.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-business-apis-resources
legacy_page_id: connect_resources_rating_waterfall_fetch.htm
fetched_at: 2026-11-25
---

# Rating Waterfall (GET)

Get the persisted rating waterfall that stores the process logs. Rating waterfall provides insights into the internal rating process.

## Resource

```
/connect/core-pricing/waterfall/{lineItemId}/{executionId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/waterfall/{Gold}/{2yHdNNEFOZr9jAe4gHS7}?tagsToFilter=UnitPrice&usageType=Rating
```

## Available Version

62.0

## HTTP Methods

GET

## Query Parameters

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `tagsTo​Filter` | String | Comma-separated tags to filter. | Optional | 62.0 |
| `usage​Type` | String | Usage type of the waterfall log record. Valid values are `Rating`; or `Pricing`—Specifies that the record type is `Pricing`. If this value is specified, the API creates a log of pricing waterfall. See [Pricing Waterfall](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_pricing_waterfall_post.htm). The default value is `Pricing`. | Optional | 62.0 |

## Response Body for GET

[Line Item Waterfall Response](./connect-responses-rating-line-item-waterfall-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-rating-waterfall-fetch.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
