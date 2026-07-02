---
page_id: connect_requests_expression_set_condition_criteria.htm
title: Expression Set Condition Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_condition_criteria.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Condition Criteria Input

Input representation of a condition criteria in an expression
set.

Root XML tag
:   `<ExpressionSetConditionCriteriaInput>`

JSON example
:   ```
    "criteria" : [ {
                    "operator" : "Equals",
                    "sequenceNumber" : 1,
                    "sourceFieldName" : "a",
                    "value" : "0",
                    "valueType" : "Literal"
                  } ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `operator` | String | Condition operator of the expression set. Valid values are:   - `Contains` - `DoesNot​Contain` - `Equals` - `GreaterThan​OrEquals` - `Greater​Than` - `IsNot​Null` - `IsNull` - `LessThan` - `LessThan​OrEquals` - `NotEqual​To` | Required | 58.0 |
    | `sequence​Number` | Integer | The sequence number of the condition in the advanced condition. | Required | 58.0 |
    | `sourceField​Name` | String | The expression set version variable associated with the condition criteria. | Required | 58.0 |
    | `value` | String | The right-hand side of the condition is specified in this field. | Required | 58.0 |
    | `valueType` | String | Criteria value type of the expression set. Valid values are:   - `Formula` - `Literal` - `Parameter` | Required | 58.0 |
