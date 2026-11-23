---
page_id: connect_requests_execution_settings_input.htm
title: Execution Settings Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_execution_settings_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Execution Settings Input

Input representation of the execution settings for a ramp deal.

## JSON Example

```
  "executionSettings": {
       "executePricing": true,
       "executeConfigRules": false
   }
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `execute​ConfigRules` | Boolean | Indicates whether to run configuration rules (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |
| `execute​Pricing` | Boolean | Indicates whether to run pricing request (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_execution_settings_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
