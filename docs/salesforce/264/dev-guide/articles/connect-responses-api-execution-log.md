---
page_id: connect-responses-api-execution-log
title: API Execution Log Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-execution-log.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-api-responses
legacy_page_id: connect_responses_api_execution_log.htm
fetched_at: 2026-11-25
---

# API Execution Log Response

Output representation of the execution log of a pricing waterfall request.

## JSON Example

```
{
  "message": {The Pricing API execution was successful.},
  "pricingElement": {
    "adjustments": [
      {
        "adjustmentType": null,
        "adjustmentValue": null
      }
    ],
    "name": "List Price",
    "elementType": "ListPrice"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String [] | Message of the API execution. | Small, 63.0 | 63.0 |
| `pricingElement` | [Adjustment Details](./connect-responses-adjustment-detail.md) | Details of the price adjustment of a pricing element. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-api-execution-log.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
