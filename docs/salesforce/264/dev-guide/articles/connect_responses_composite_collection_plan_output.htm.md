---
page_id: connect_responses_composite_collection_plan_output.htm
title: Composite Collection Plan
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_composite_collection_plan_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Composite Collection Plan

Output representation of the results for each collection
plan.

## JSON Example

```
{
  "results": [
    {
      "collectionPlanId": "1Eu000000000001AAA",
      "collectionPlanItemIds": [
        "1Ev000000000001AAA",
        "1Ev000000000002AAA"
      ],
      "isSuccess": true,
      "errors": null
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `results` | [Collection Plan](./connect_responses_collection_plan_output.htm.md "Output representation of the result of a single collection plan creation request.")[] | List of results, with one result for each collection plan in the request. | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_composite_collection_plan_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
