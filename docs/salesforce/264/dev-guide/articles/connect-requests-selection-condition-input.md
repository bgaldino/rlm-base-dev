---
page_id: connect-requests-selection-condition-input
title: Selection Condition Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-selection-condition-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-requests
legacy_page_id: connect_requests_selection_condition_input.htm
fetched_at: 2026-11-25
---

# Selection Condition Input

Input representation of the criteria that’s used to determine which sequencing policy is applied to a record. The criteria stores the conditions based on any standard or custom fields of the record.

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
| `condition​Number` | Integer | Unique number that’s assigned to a condition in a sequence policy. | Required | 65.0 |
| `filterField` | String | Field used in the filter condition. | Required | 65.0 |
| `filterValue` | String | Value in the filter condition. | Required | 65.0 |
| `operator` | String | Relational operator that’s used to compare the filter field with the filter value. Valid values are `Equals` or `NotEquals`. | Required | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-selection-condition-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
