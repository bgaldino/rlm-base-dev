---
page_id: connect_requests_decision_table_row_list_input.htm
title: Decision Table Row List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_row_list_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_requests.htm
fetched_at: 2026-11-23
---

# Decision Table Row List Input

Input representation of the data for a row in the CSV based decision
table that has to be added or updated.

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

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `action` | String | Action to perform on this row. Valid values are:   - `Create` - `Update` | Optional | 62.0 |
| `id` | String | ID of the decision table tow. | Optional | 62.0 |
| `rowdata` | Map<String, Object> | Key value pair of the decision table row. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_row_list_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
