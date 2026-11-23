---
page_id: connect_requests_selection_condition_input.htm
title: Selection Condition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_selection_condition_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-11-23
---

# Selection Condition Input

Input representation of the criteria that's used to determine which sequencing policy is applied to a record. The criteria stores the conditions based on any standard or custom fields of the record.

## JSON Example

```
{
  "selectionCondition": [
    {
      "filterField": "AppType",
      "operator": "Equals",
      "filterValue": "RLM",
      "conditionNumber": 1
    },
    {
      "filterField": "Status",
      "operator": "Equals",
      "filterValue": "Posted",
      "conditionNumber": 2
    },
    {
      "filterField": "LegalEntity",
      "operator": "Equals",
      "filterValue": "US",
      "conditionNumber": 3
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `condition​Number` | Integer | Unique number that's assigned to a condition in a sequence policy. | Required | 65.0 |
| `filterField` | String | Field used in the filter condition. | Required | 65.0 |
| `filterValue` | String | Value in the filter condition. | Required | 65.0 |
| `operator` | String | Relational operator that's used to compare the filter field with the filter value. Valid values are `Equals` or `NotEquals`. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_selection_condition_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
