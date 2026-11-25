---
page_id: connect-resources-get-rate-plan
title: Rate Plan (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-rate-plan.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-business-apis-resources
legacy_page_id: connect_resources_get_rate_plan.htm
fetched_at: 2026-11-25
---

# Rate Plan (GET)

Get a rate plan for a specified set of context input. Use this API to retrieve rate cards, rate card entries, and related adjustments based on the filter criteria for the context input.

Keep these considerations in mind when you use this API.

- This API request supports one pricebook and one sellable product.

- The ID of the product is required to invoke this API.

- Invoke this API even if a hydrated context is available to fetch the rate card, rate card entry, and adjustment details.

## Special Access Rules

The org must have the Rate Management: Run Time User permission set to use this API. Additionally, the org must also have a default usage rating discovery procedure defined in the Revenue Settings from Setup.

## Resource

```
/connect/core-rating/rate-plan
```

## Resource Example

```
https://{yourInstance}.salesforce.com​/services​/data/v68.0/connect/​core-rating/rate-plan​?contextId=858a3ad3e5a0e​5c319652a6ab92f6​fdb2b4fa8be72b390506​d014596c6da62c9&procedure​ApiName=Sample​Procedure
```

## Available Version

62.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context to specify as an input to the procedure. | Required | 62.0 |
| `procedure​ApiName` | String | API name of the procedure to be executed. | Required | 62.0 |

## Response Body for GET

[Rate Plan Response](./connect-responses-rate-plan-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-get-rate-plan.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
