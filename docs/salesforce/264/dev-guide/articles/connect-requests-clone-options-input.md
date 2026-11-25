---
page_id: connect-requests-clone-options-input
title: Clone Options Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-clone-options-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_clone_options_input.htm
fetched_at: 2026-11-25
---

# Clone Options Input

Input representation of the options to clone a sales transaction.

## JSON Example

This is a sample request to clone all line items in a ramped group within a sales transaction.

```
{
  "recordIds": ["0QLxx0000004CBYGA2"],
  "salesTransactionId": "0Q0xx0000004CE0CAM",
  "options": {
    "lineScope": "AllLines"
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `recordTypeId` | String | ID of the record type related to the record to clone. | Optional | 65.0 |
| `lineScope` | String | Specifies the scope for cloning a ramp segment. You can clone only the last ramp segment. This property determines which line items must be cloned and added to the cloned segment. Valid values are `AllLines`—Specifies whether all line items in a ramped group must be cloned or `RampedLinesOnly`—Specifies whether only the ramped line items must be cloned. A segment identifier is created for the newly cloned line items, ensuring date continuity between the existing and cloned segment. | Optional | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-clone-options-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
