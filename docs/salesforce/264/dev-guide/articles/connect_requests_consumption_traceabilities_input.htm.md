---
page_id: connect_requests_consumption_traceabilities_input.htm
title: Consumption Traceabilities Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_consumption_traceabilities_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_requests.htm
fetched_at: 2026-11-23
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

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_consumption_traceabilities_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
