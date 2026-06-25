---
page_id: connect_requests_expression_set_advanced_condition_step.htm
title: Expression Set Advanced Condition Step Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_advanced_condition_step.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Advanced Condition Step Input

Input representation of an advanced condition step in an expression
set.

Root XML tag
:   `<ExpressionSetAdvancedConditionStepInput>`

JSON example
:   ```
    "advancedCondition" : {
                "conditionLogic" : "1",
                  "criteria" : [ {
                    "operator" : "Equals",
                    "sequenceNumber" : 1,
                    "sourceFieldName" : "a",
                    "value" : "0",
                    "valueType" : "Literal"
                  } ],
                "resultParameter" : "condition_output__1"
              }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `condition​Logic` | String | Condition that’s defined for the advanced condition. For example, if all conditions are met or any of the conditions are met. | Required | 58.0 |
    | `criteria` | [Expression Set Condition Criteria Input](./connect_requests_expression_set_condition_criteria.htm.md "Input representation of a condition criteria in an expression set.")[] | List of condition criteria in an expression set. | Required | 58.0 |
    | `result​Parameter` | String | Expression set definition version variable associated with the result of the step. | Required | 58.0 |
