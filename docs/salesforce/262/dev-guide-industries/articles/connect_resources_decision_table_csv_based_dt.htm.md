---
page_id: connect_resources_decision_table_csv_based_dt.htm
title: CSV Based Decision Table (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_csv_based_dt.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_resources.htm
fetched_at: 2026-06-25
---

# CSV Based Decision Table (GET)

Fetch paginated data from a CSV based decision table. This resource is responsible for
managing rows in a Decision Table.

Resource
:   ```
    /connect/business-rules/decision-table/${decisionTableId}/data
    ```

Example for GET
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/decision-table/0lDxx0000000001EAA/data?filter=AssetLevel:101
    ```

Example for POST
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/decision-table/0lDxx0000000001EAA/data
    ```

Available version
:   62.0

HTTP methods
:   GET POST

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `filter` | String | Filters applied to rows based on column criteria. | Optional | 62.0 |
    | `limit` | Integer | Limits the number of records viewed at a time. The default value is `20`. | Optional | 62.0 |
    | `offset` | Integer | Token that represents the page offset for pagination. Use this value with the pageSize parameter to indicate where the page starts. The maximum offset is `100` and the default is `0`. | Optional | 62.0 |

Response body for GET
:   [Decision Table Rows List](./connect_responses_decision_table_rows_list_output.htm.md "Output representation of the rows in relation to the decision table, including current state of pagination.")

Request body for POST
:   JSON example
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

Request parameters for POST
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `rows​Input` | Object |  |  | 62.0 |

Response body for POST
:   [Decision Table Data](./connect_responses_decision_table_data_output.htm.md "Output representation of the status of an action performed.")
