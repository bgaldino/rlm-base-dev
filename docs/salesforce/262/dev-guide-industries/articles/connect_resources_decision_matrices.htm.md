---
page_id: connect_resources_decision_matrices.htm
title: Decision Matrices
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrices.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-06-25
---

# Decision Matrices

Get a list of decision matrices ( also known as calculation matrix)
based on a search text. The API returns a maximum of ten decision matrices records that
contain the specified keyword.

Resource
:   ```
    /connect/omnistudio/decision-matrices
    ```

Example URI
:   ```
    /services/data/v53.0/connect/omnistudio/decision-matrices?searchKey=Test
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `searchKey` | String | The user-entered search text to retrieve a list of decision matrices. |  | 53.0 |

Response body for GET
:   [Decision Matrix Result List](./connect_responses_decision_matrix_result_list.htm.md "Output representation of the decision matrix result list.")
