---
page_id: connect_responses_decision_table_rows_list_output.htm
title: Decision Table Rows List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_rows_list_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-06-25
---

# Decision Table Rows List

Output representation of the rows in relation to the decision table, including current
state of pagination.

Sample Output
:   ```
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
| `rows` | [Decision Table Row](./connect_responses_decision_table_row_output.htm.md "Output representation to describe the output of a decision table row.")[] | List of rows returned in response to the API request. | Small, 62.0 | 62.0 |
| `totalRows` | Integer | Total number of rows. | Small, 62.0 | 62.0 |
