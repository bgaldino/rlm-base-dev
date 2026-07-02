---
page_id: connect_requests_expression_set_condition_expression_step.htm
title: Expression Set Condition Expression Step
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_condition_expression_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Condition Expression Step

Input representation of an expression set condition
step.

Root XML tag
:   `<ExpressionSetConditionExpressionStepInput>`

JSON example
:   ```
    "conditionExpression": {
                    "expression": "productName == 'iPhone' && City == 'Los Angeles'",
                    "resultParameter": "condition_output__1"
                  }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `expression` | String | Expression that’s defined for the step. | Required | 58.0 |
    | `result​Parameter` | String | Expression set version variable associated with the result of the step. | Required | 58.0 |
