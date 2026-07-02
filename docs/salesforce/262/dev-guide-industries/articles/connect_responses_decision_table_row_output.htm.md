---
page_id: connect_responses_decision_table_row_output.htm
title: Decision Table Row
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_row_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-06-25
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
