---
page_id: connect-resources-collections-composite-collection-plan
title: Composite Collection Plan Creation (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-collections-composite-collection-plan.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_collections_composite_collection_plan.htm
fetched_at: 2026-11-25
---

# Composite Collection Plan Creation (POST)

Create one or more collection plans, each with its collection plan items, in a single request.

This API creates each collection plan in the request together with its nested collection plan items. Each collection plan runs independently, so the request can partially succeed across plans. Within a single collection plan, if any of its collection plan items fail to create, the parent collection plan is rolled back. The response returns a result for each collection plan in the request that indicates whether the collection plan was created successfully and includes any errors.

A request can include up to 200 collection plans, and each collection plan can include up to 200 collection plan items.

## Special Access Rules

Set up collections and enable invoicing in your org.

## Resource

```
/connect/collections/composite-collection-plan
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/collections/composite-collection-plan
```

## Available Version

68.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `collection​Plans` | [Collection Plan Input](./connect-requests-collection-plan-input.md)[] | List of collection plans to create. Each plan can include a nested list of collection plan items to create with it. Specify at least 1 collection plan and up to 200 collection plans. Each collection plan can include up to 200 collection plan items. | Required | 68.0 |

## Response Body for POST

[Composite Collection Plan](./connect-responses-composite-collection-plan-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-collections-composite-collection-plan.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
