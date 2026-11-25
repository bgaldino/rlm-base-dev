---
page_id: connect-requests-consumption-traceabilities-input
title: Consumption Traceabilities Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-consumption-traceabilities-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-requests
legacy_page_id: connect_requests_consumption_traceabilities_input.htm
fetched_at: 2026-11-25
---

# Consumption Traceabilities Input

Input representation of the details of the liable summary IDs that are used to trace the consumption.

## JSON Example

```
{
  "liableSummaryIds": [
    "1HG000000000001"
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `liableSummaryIds` | String[] | List of liable summary IDs to trace the consumption. | Required | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-consumption-traceabilities-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
