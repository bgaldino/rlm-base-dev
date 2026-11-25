---
page_id: connect-responses-decision-table-rows-list-output
title: Decision Table Rows List
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-rows-list-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-responses
legacy_page_id: connect_responses_decision_table_rows_list_output.htm
fetched_at: 2026-11-25
---

# Decision Table Rows List

Output representation of the rows in relation to the decision table, including current state of pagination.

**Sample Output**

: 

```
{
  "rows": [
    {
      "id": "1FIxx0000004CCG",
      "rowData": {
        "AssetLevel": "101",
        "City": "city1"
      }
    }
  ],
  "totalRows": 3
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `rows` | [Decision Table Row](./connect-responses-decision-table-row-output.md)[] | List of rows returned in response to the API request. | Small, 62.0 | 62.0 |
| `totalRows` | Integer | Total number of rows. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-rows-list-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
