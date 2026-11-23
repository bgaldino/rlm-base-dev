---
page_id: connect_resources_execution_logs.htm
title: API Execution Logs (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_execution_logs.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_business_apis_rest_references.htm
fetched_at: 2026-11-23
---

# API Execution Logs (GET)

Get the log details of a pricing API execution record by using the execution ID.

## Resource

```
/connect/core-pricing/apiexecutionlogs/executionId
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/core-pricing/apiexecutionlogs/29646938297972
```

## Available Version

63.0

## HTTP Methods

GET

## Path Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | ID of the pricing process execution record. | Required | 63.0 |

## Response Body for GET

[Pricing Execution Waterfall Response](./connect_responses_api_execution_waterfall_response.htm.md "Output representation of the execution process that's associated with a pricing waterfall.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_execution_logs.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
