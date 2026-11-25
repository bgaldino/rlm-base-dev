---
page_id: connect-requests-pricing-request
title: Pricing Request Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-request.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-requests
legacy_page_id: connect_requests_pricing_request.htm
fetched_at: 2026-11-25
---

# Pricing Request Input

Input representation of a pricing request.

## JSON Example

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configuration​Overrides` | [Configuration Override Input](./connect-requests-configuration-override-input.md) | Parameters to override pricing configuration. | Optional | 60.0 |
| `procedure​Name` | String | Name of the pricing procedure. | Optional | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-pricing-request.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
