---
page_id: connect-responses-warnings-output
title: Warnings
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-warnings-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Usage Management
parent_page: usage-management-business-apis-responses
legacy_page_id: connect_responses_warnings_output.htm
fetched_at: 2026-11-25
---

# Warnings

Output representation of a group of warning messages with the same warning code.

## JSON Example

This example shows a group of warning messages with the same warning code.

```
{
  "warnings": [
    {
      "warningCode": "PERFORMANCE_SUBOPTIMAL",
      "warningMessages": [
        {
          "warningMessage": "PUR and RCE date ranges could be optimized for better performance",
          "warningDetails": []
        }
      ]
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `warningCode` | String | Standardized warning code. For example, `PERFORMANCE_SUBOPTIMA` L. | Big, 66.0 | 66.0 |
| `warningMessages` | [Warning Message](./connect-responses-warning-message-output.md)[] | List of warning messages for records that triggered with this warning. | Big, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-warnings-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
