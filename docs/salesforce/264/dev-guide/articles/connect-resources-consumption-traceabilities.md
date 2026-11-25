---
page_id: connect-resources-consumption-traceabilities
title: Consumption Traceabilities (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-consumption-traceabilities.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-resources
legacy_page_id: connect_resources_consumption_traceabilities.htm
fetched_at: 2026-11-25
---

# Consumption Traceabilities (POST)

Get a comprehensive breakdown of overage charges and resource drawdown, enabling you to view information that’s applicable to specific invoice lines.

This API provides an automated, clear, and traceable breakdown of all charges with details of specific rates, tiers, and discounts.

## Resource

```
/revenue/usage-management/consumption/actions/trace
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/revenue/usage-management/consumption/actions/trace
```

## Available Version

66.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "liableSummaryIds": [
    "1HG000000000001"
  ]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `liableSummaryIds` | String[] | List of liable summary IDs to trace the consumption. | Required | 66.0 |

## Response Body for POST

[Consumption Traceabilities](./connect-responses-consumption-traceabilities-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-consumption-traceabilities.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
