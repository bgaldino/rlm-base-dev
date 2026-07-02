---
page_id: connect_resources_decision_matrix_columns.htm
title: Decision Matrix Columns
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrix_columns.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix Columns

Retrieve a list of or manage columns in a decision matrix. Use this
resource to add new columns, or update or delete existing columns in a decision
matrix.

Resource
:   ```
    /connect/omnistudio/decision-matrices/${matrixId}/columns
    ```

Example
:   ```
    /services/data/v53.0/connect/omnistudio/decision-matrices/0lIR000000000u0MAA/columns
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET, POST

Path parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `matrixId` | String | The ID of the decision matrix record. | Required | 53.0 |

Response body for GET
:   [Decision Matrix Columns Output](./connect_responses_decision_matrix_columns_output.htm.md "Output representation of columns of a decision matrix.")

Request body for POST
:   JSON example
    :   Add a column:

        ```
        {
           "columns" : [ {
              "apiName" : "Name",
              "columnType" : "Input",
              "dataType" : "Text",
              "displaySequence" : 4,
              "name" : "Name"
           }]
        }
        ```
    :   Delete a column:

        ```
        {
           "columns" : [ {
              "action" : "delete",
              "id" : "0lJR0000000014bMAA"
           }]
        }
        ```
    :   Update a column:

        ```
        {
           "columns" : [ {
              "id" : "0lJR0000000014hMAA",
              "action" : "update",
              "columnType" : "Input",
              "name" : "First Name"
           }]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `columns` | [Decision Matrix Column Input](./connect_requests_decision_matrix_column.htm.md "Input representation of the information required to add, update, or delete columns in a decision matrix.")[] | List of columns to be added, updated, or deleted in a decision matrix. | Required | 53.0 |

Response body for POST
:   [Decision Matrix Output](./connect_responses_decision_matrix_output.htm.md "Output representation the action performed on a decision matrix version.")
