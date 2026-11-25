---
page_id: connect-requests-decision-table-rows-list-input
title: Decision Table Rows List Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-rows-list-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-requests
legacy_page_id: connect_requests_decision_table_rows_list_input.htm
fetched_at: 2026-11-25
---

# Decision Table Rows List Input

Input representation of the request to update rows in a CSV based decision table.

## JSON Example

```
{
  "rows": [
    {
      "id": "1FIxx0000004CSOGA2",
      "rowData": {
        "City": "City3",
        "AssetLevel": "300"
      },
      "action": "update"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rows` | [Decision Table Row Input](./connect-requests-decision-table-row-list-input.md)[] | List of rows to be updated or added. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-rows-list-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
