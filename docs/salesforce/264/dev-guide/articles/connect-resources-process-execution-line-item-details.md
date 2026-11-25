---
page_id: connect-resources-process-execution-line-item-details
title: Pricing Process Execution for Line Items (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-process-execution-line-item-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_process_execution_line_item_details.htm
fetched_at: 2026-11-25
---

# Pricing Process Execution for Line Items (GET)

Get the pricing execution details for the line items of a pricing process by using the execution ID and execution type.

## Resource

```
/connect/core-pricing/pricing-process-execution/lineitems/{executionId}/{executionType}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/pricing-process-execution/lineitems/{29646938297972}/{Pricing_Line}
```

## Available Version

63.0

## HTTP Methods

GET

## Path Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | ID of the pricing process execution record. | Required | 63.0 |
| `executionType` | String | Type of the execution that’s defined internally within the pricing API. Valid values are `Pricing_Line` or `Discovery_Line`. | Required | 63.0 |

## Response Body for GET

[Pricing Process Execution Details for Line Items](./connect-responses-process-execution-line-item-details-get-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-process-execution-line-item-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
