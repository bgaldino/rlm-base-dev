---
page_id: connect-resources-execution-logs
title: API Execution Logs (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-execution-logs.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_execution_logs.htm
fetched_at: 2026-11-25
---

# API Execution Logs (GET)

Get the log details of a pricing API execution record by using the execution ID.

## Resource

```
/connect/core-pricing/apiexecutionlogs/{executionId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/apiexecutionlogs/{29646938297972}
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

[Pricing Execution Waterfall Response](./connect-responses-api-execution-waterfall-response.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-execution-logs.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
