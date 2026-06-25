---
page_id: connect_responses_bre_decision_matrix_lookup_result.htm
title: Decision Matrix Lookup Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_decision_matrix_lookup_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-06-25
---

# Decision Matrix Lookup Result

Output representation of the individual output of a decision matrix
version lookup.

JSON example
:   ```
    {
      "outputs": [
        {
          "results": [],
          "error": "Input Data is Missing"
        },
        {
          "results": [
            {
              "name": "premium",
              "value": "2400"
            },
            {
              "name": "tax",
              "value": "300"
            }
          ]
        },
        {
          "results": [],
          "error": "There is no output for the given input data"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `outputs` | [Decision Matrix Lookup Basic Result](./connect_responses_decision_matrix_lookup_basic_result.htm.md "Results from a Decision Matrix lookup using a single input.")[] | List of outputs returned by a decision matrix. An output may contain multiple variables. | Small, 55.0 | 55.0 |
