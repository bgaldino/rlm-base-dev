---
page_id: connect_responses_decision_table_row_output.htm
title: Decision Table Row
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_row_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-11-23
---

# Decision Table Row

Output representation to describe the output of a decision table row.

Sample Output
:   ```
    {
      "rows": {
        "id": "1FIxx0000004CCG",
        "rowData": {
          "AssetLevel": "101",
          "City": "city1"
        }
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the decision table row. | Small, 62.0 | 62.0 |
| `rowData` | Map<String, Object> | Key value pair of the decision table row. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_row_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
