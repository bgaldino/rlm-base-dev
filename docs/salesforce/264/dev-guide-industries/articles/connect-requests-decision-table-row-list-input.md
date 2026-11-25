---
page_id: connect-requests-decision-table-row-list-input
title: Decision Table Row List Input
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-row-list-input.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-requests
legacy_page_id: connect_requests_decision_table_row_list_input.htm
fetched_at: 2026-11-25
---

# Decision Table Row List Input

Input representation of the data for a row in the CSV based decision table that has to be added or updated.

## JSON Example

```
{
  "id": "1FIxx0000004CSOGA2",
  "rowData": {
    "City": "City3",
    "AssetLevel": "300"
  },
  "action": "update"
}
```

## Properties

- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | Action to perform on this row. Valid values are: `Create``Update` | Optional | 62.0 |
| `id` | String | ID of the decision table tow. | Optional | 62.0 |
| `rowdata` | Map<String, Object> | Key value pair of the decision table row. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-requests-decision-table-row-list-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
