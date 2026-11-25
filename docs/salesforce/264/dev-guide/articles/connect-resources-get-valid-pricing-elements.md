---
page_id: connect-resources-get-valid-pricing-elements
title: Pricing Recipe Valid Elements (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-valid-pricing-elements.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_get_valid_pricing_elements.htm
fetched_at: 2026-11-25
---

# Pricing Recipe Valid Elements (GET)

Get the list of valid pricing element type API names for a given Pricing Usage Sub Type.

## Resource

```
/connect/core-pricing/revenue/pricing-recipe/valid-elements
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/revenue/pricing-recipe/valid-elements?pricingUsageSubType=RevenueCloud
```

## Available Version

68.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `pricingUsageSubType` | String | Pricing usage subtype to retrieve the valid element types for. Must match an entry in the PricingUsageSubType picklist. For example, `RevenueCloud`, `Loyalty`, `LifeSciences`, and `Commercial`. | Required | 68.0 |

## Response Body for GET

[Pricing Recipe Valid Elements](./connect-responses-pricing-valid-elements-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-valid-pricing-elements.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
