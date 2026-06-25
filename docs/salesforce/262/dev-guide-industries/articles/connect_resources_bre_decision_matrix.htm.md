---
page_id: connect_resources_bre_decision_matrix.htm
title: Decision Matrix Lookup (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_bre_decision_matrix.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-06-25
---

# Decision Matrix Lookup (POST)

Performs a lookup on decision matrix rows based on the input values
provided, and returns the row’s output.

Resource
:   ```
    /connect/business-rules/decision-matrices/${matrixName}
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/vXX.X/connect
    /business-rules/decision-matrices/InsurancePremium
    ```

Available version
:   55.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "inputs": [
            {
              "input": [
                {
                  "name": "Premium",
                  "value": "2400"
                }
              ]
            },
            {
              "input": [
                {
                  "name": "Tenure",
                  "value": "10"
                }
              ]
            }
          ],
          "options": {
            "effectiveDate": "2022-12-03T10:15:30Z"
          }
        }
        ```
    :   Here, `Premium` and `Tenure` are column
        headers in the matrix, and `2400` and `10` are
        values of a cell in the column.

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `inputs` | [Decision Matrix Input](./connect_requests_decision_matrix_input.htm.md "Input representation of the inputs passed to a decision matrix for lookup.") | List of inputs passed to a decision matrix. An input may contain multiple variables. | Required | 55.0 |
        | `options` | [Decision Matrix Options Input](./connect_requests_decision_matrix_options.htm.md "Input representation of the options used to look up a decision matrix.") | The lookup options for a decision matrix. | Optional | 55.0 |

Response body for POST
:   [Decision Matrix Lookup Result](./connect_responses_bre_decision_matrix_lookup_result.htm.md "Output representation of the individual output of a decision matrix version lookup.")
