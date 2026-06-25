---
page_id: connect_requests_expression_set_assignment_step.htm
title: Expression Set Assignment Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_assignment_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Assignment Step Input

Input representation of an assignment step in an expression
set.

Root XML tag
:   `<ExpressionSetAssignmentStepInput>`

JSON example
:   ```
    "assignment" : {
                "assignedParameter" : "b",
                "expression" : "100"
              }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `assigned​Parameter` | String | Expression set version variable that’s present on the right side of the calculation step. | Required | 58.0 |
    | `expression` | String | Expression that’s present on the left side of the calculation step. | Required | 58.0 |
