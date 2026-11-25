---
page_id: connect-resources-pricing-process-execution
title: Pricing Process Execution (GET)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-pricing-process-execution.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-business-apis-rest-references
legacy_page_id: connect_resources_pricing_process_execution.htm
fetched_at: 2026-11-25
---

# Pricing Process Execution (GET)

Get the execution details of a pricing process by using the execution ID.

## Resource

```
/connect/core-pricing/pricing-process-execution/{executionId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/core-pricing/pricing-process-execution/{29646938297972}
```

## Available Version

63.0

## HTTP Methods

GET

## Path Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionId` | String | ID of the pricing process execution record. The ID is generated each time a pricing process is executed. | Required | 63.0 |

## Query Parameter for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `executionType` | String | Type of execution that’s defined internally within the pricing API. Valid values are `API_Execution`, `Discovery`—Discovery procedure, `Discovery_Line`—Discovery procedure for the line items, `Pricing`—Pricing procedure, or `Pricing_Line`—Pricing procedure for the line items. If the `executionType` parameter isn’t specified, the API retrieves records for all the execution types that are associated with the specified execution ID. | Optional | 63.0 |

## Response Body for GET

[Pricing Process Execution Response](./connect-responses-pricing-process-execution-get-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-pricing-process-execution.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
