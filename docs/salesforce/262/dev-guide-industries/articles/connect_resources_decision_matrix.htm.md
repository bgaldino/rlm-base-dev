---
page_id: connect_resources_decision_matrix.htm
title: Decision Matrix
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_matrix.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix

Retrieve the details for a given decision matrix record (also known as
calculation matrix).

Resource
:   ```
    /connect/omnistudio/decision-matrices/${matrixId}
    ```

Example URI
:   ```
    /services/data/v53.0/connect/omnistudio/decision-matrices/0lIx0000000000zEAA
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET

Response body for GET
:   [Decision Matrix Result](./connect_responses_decision_matrix_result.htm.md "Output representation of the decision matrix details.")
