---
page_id: connect-resources-pricing-data-sync
title: Pricing Data Sync (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-pricing-data-sync.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_pricing_data_sync.htm
fetched_at: 2026-11-25
---

# Pricing Data Sync (GET)

Sync pricing data to ensure that the lookup tables contain the latest pricing data.

To partially synchronize pricing data, use the Decision Table Refresh Action in a Flow. See [Decision Table Refresh Action](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/dt_actions_refresh_decision_table.htm).

## Resource

```
/connect/core-pricing/sync/{pricingSyncOrigin}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/sync/{syncData}
```

This example shows a sample resource to filter by pricing recipe.

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/sync/syncData?pricingRecipeId={12Gxx0000005IzhEAE}
```

## Available Version

60.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricing​RecipeId` | String | ID of the pricing recipe whose decision tables you want to sync. If not specified, the default pricing recipe is used. | Optional | 67.0 |

## Response Body for GET

[Pricing Generic Response](./connect-responses-pricing-generic-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-pricing-data-sync.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
