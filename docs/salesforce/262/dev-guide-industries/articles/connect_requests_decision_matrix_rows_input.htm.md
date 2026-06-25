---
page_id: connect_requests_decision_matrix_rows_input.htm
title: Decision Matrix Rows Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_rows_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix Rows Input

Input representation of the information to manage rows in relation to
the decision matrix version.

JSON Example
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
