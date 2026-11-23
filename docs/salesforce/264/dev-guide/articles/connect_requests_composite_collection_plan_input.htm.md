---
page_id: connect_requests_composite_collection_plan_input.htm
title: Composite Collection Plan Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_composite_collection_plan_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Composite Collection Plan Input

Input representation of one or more collection plans, each with its
optional nested collection plan items.

## JSON Example

```
{
  "collectionPlans": [
    {
      "accountId": "001xx000003DGXYA2",
      "contactId": "003xx000004TXYZA1",
      "initialDueAmount": 7500.00,
      "collectionPlanSegment": "High Risk",
      "dueDate": "2026-06-15",
      "collectionPlanReasonId": "0cR000000000001",
      "usageType": "Billing",
      "overdueRiskIndicator": "High",
      "collectionPlanItems": [
        {
          "invoiceId": "inv000000000001"
        },
        {
          "invoiceId": "inv000000000002"
        }
      ]
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `collection​Plans` | [Collection Plan Input](./connect_requests_collection_plan_input.htm.md "Input representation of a single collection plan, including its optional nested collection plan items.")[] | List of collection plans to create. Each plan can include a nested list of collection plan items to create with it. Specify at least 1 collection plan and up to 200 collection plans. Each collection plan can include up to 200 collection plan items. | Required | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_composite_collection_plan_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
