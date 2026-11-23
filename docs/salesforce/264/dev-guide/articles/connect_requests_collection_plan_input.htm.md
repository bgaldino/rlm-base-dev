---
page_id: connect_requests_collection_plan_input.htm
title: Collection Plan Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_collection_plan_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Collection Plan Input

Input representation of a single collection plan, including its
optional nested collection plan items.

## JSON Example

```
{
  "accountId": "001xx000003DGXYA2",
  "contactId": "003xx000004TXYZA1",
  "initialDueAmount": 7500,
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
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `accountId` | String | ID of the account associated with the collection plan. | Required | 68.0 |
| `collection​PlanItems` | [Collection Plan Item Input](./connect_requests_collection_plan_item_input.htm.md "Input representation of a single collection plan item to create under a collection plan.")[] | List of collection plan items to create under this collection plan. You can specify up to 200 collection plan items. If an item fails to create, the parent collection plan is rolled back. | Optional | 68.0 |
| `collection​Plan​ReasonId` | String | ID of the collection plan reason associated with the collection plan. | Optional | 68.0 |
| `collection​Plan​Segment` | String | Predefined segment associated with the collection plan. The segment is derived from criteria such as the collection amount and the number of days past due. Because this segment is a dynamic value that you define, the valid values vary by org. | Optional | 68.0 |
| `contactId` | String | ID of the contact associated with the collection plan. | Optional | 68.0 |
| `dueDate` | String | Date by which the payment toward the outstanding amount is expected, in `YYYY-MM-DD` format. | Optional | 68.0 |
| `initialDue​Amount` | Double | Initial due amount of the collection. | Optional | 68.0 |
| `overdue​Risk​Indicator` | String | Overdue risk level for the collection plan. Valid values are:  - `High` - `Low` - `Medium` | Optional | 68.0 |
| `usage​Type` | String | Usage type of the collection plan. Valid value is `Billing`. | Required | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_collection_plan_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
