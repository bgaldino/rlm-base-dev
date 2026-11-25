---
page_id: connect-responses-collection-plan-output
title: Collection Plan
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-collection-plan-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_collection_plan_output.htm
fetched_at: 2026-11-25
---

# Collection Plan

Output representation of the result of a single collection plan creation request.

## JSON Example

```
{
  "collectionPlanId": "1Eu000000000001AAA",
  "collectionPlanItemIds": [
    "1Ev000000000001AAA",
    "1Ev000000000002AAA"
  ],
  "isSuccess": true,
  "errors": null
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `collection​PlanId` | String | ID of the created collection plan. This value is null if the creation failed. | Big, 68.0 | 68.0 |
| `collection​Plan​ItemIds` | String[] | IDs of the created collection plan items. This value is null if the creation failed. | Big, 68.0 | 68.0 |
| `errors` | [Collection Plan Error](./connect-responses-collection-plan-error.md)[] | List of errors that occurred while creating the collection plan. This value is null if the creation succeeded. | Big, 68.0 | 68.0 |
| `isSuccess` | Boolean | Indicates whether collection plan creation was successful (`true`) or not (`false`). | Big, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-collection-plan-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
