---
page_id: connect-resources-price-context
title: Price Context (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-price-context.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_price_context.htm
fetched_at: 2026-11-25
---

# Price Context (POST)

Perform a pricing request by using the instance ID of a context.

If price waterfall is disabled from Salesforce Pricing Setup in your org, this API doesn’t return the waterfall details. You can use the [Price Waterfall API](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_pricing_waterfall_fetch.htm) to retrieve the waterfall details if price waterfall persistence is enabled in Salesforce Pricing Setup.

## Resource

```
/connect/core-pricing/price-contexts/{contextid}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/price-contexts/{0U3RM00000000SR0AY}
```

## Available Version

60.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "configurationOverrides": {
       "skipWaterfall": true,
       "useSessionScopedContext": true,
       "persistContext": true,
       "taggedData": false
    }
    "procedureName": "ES1"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Overrides` | [Configuration Override Input](./connect-requests-configuration-override-input.md) | Parameters to override pricing configuration. | Optional | 60.0 |
| `procedure​Name` | String | Name of the pricing procedure. | Optional | 60.0 |

## Response Body for POST

[Pricing Response](./connect-responses-pricing-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-price-context.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
