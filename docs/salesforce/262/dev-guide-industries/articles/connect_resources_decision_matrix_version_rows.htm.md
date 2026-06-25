---
page_id: connect_resources_decision_matrix_version_rows.htm
title: Decision Matrix Version Rows
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrix_version_rows.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix Version Rows

Retrieve a paginated list of or manage rows in a decision matrix
version. Use this resource to add new rows, or update or delete existing rows in a decision
matrix version.

Resource
:   ```
    /connect/omnistudio/decision-matrices/${matrixId}/versions/${versionId}/rows
    ```

Example
:   ```
    /services/data/v53.0/connect/omnistudio/decision-matrices/0lIR000000000u0MAA
    /versions/0lNR000000000rFMAQ/rows
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
    | `versionId` | String | The ID of the decision matrix version record. | Required | 53.0 |

Query parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `file` | Boolean | Indicates whether to get the rows by generating a CSV file for downloading (`true`) or fetching the rows in JSON format (`false`). The default value is `false`. | Optional | 53.0 |

Response body for GET
:   [Decision Matrix Rows Output](./connect_responses_decision_matrix_rows_output.htm.md "Output representation of rows of a decision matrix version.")

Request body for POST
:   JSON Example
    :   Add a row:

        ```
        {
          "rows": [
            {
              "rowData": {
                "Age": "45",
                "Gender": "F",
                "Premium": "2000"
              }
            }
          ]
        }
        ```
    :   Delete a row:

        ```
        {
          "rows": [
            {
              "id": "a1j5w000006D04uAAC",
              "action": "delete",
              "rowData": {
                "Age": "45",
                "Gender": "F",
                "Premium": "2000"
              }
            }
          ]
        }
        ```
    :   Update a row:

        ```
        {
          "rows": [
            {
              "id": "a1j5w000006D04uAAC",
              "action": "update",
              "rowData": {
                "Age": "45",
                "Gender": "F",
                "Premium": "1500"
              }
            }
          ]
        }
        ```
    :   Add row using a CSV file:
    :   ```
        {
           "fileId" : "f1j5w000005D04uFGC"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `fileId` | String | The ID of the [Content Document Version](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_contentversion.htm) that contains the rows details to be added or updated in a decision matrix version. | Optional Note Note This field is required if you’re using a CVS file to add or update rows. | 53.0 |
        | `rows` | [Decision Matrix Row Input](./connect_requests_decision_matrix_row_input.htm.md "Input representation of the information required to add, update, or delete rows in a decision matrix version.")[] | List of rows to be added, updated, or deleted in a decision matrix version. | Required | 53.0 |

Response body for POST
:   [Decision Matrix Output](./connect_responses_decision_matrix_output.htm.md "Output representation the action performed on a decision matrix version.")
