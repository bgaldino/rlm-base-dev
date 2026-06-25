---
page_id: connect_requests_decision_table_rows_list_input.htm
title: Decision Table Rows List Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_rows_list_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_requests.htm
fetched_at: 2026-06-25
---

# Decision Table Rows List Input

Input representation of the request to update rows in a CSV based
decision table.

JSON example
:   ```
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

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `rows` | [Decision Table Row Input](./connect_requests_decision_table_row_list_input.htm.md "Input representation of the data for a row in the CSV based decision table that has to be added or updated.")[] | List of rows to be updated or added. | Required | 62.0 |
