---
page_id: connect_requests_expression_set_version_variable.htm
title: Expression Set Version Variable Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_expression_set_version_variable.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Expression Set Version Variable Input

Input representation of a variable in an expression set
version.

Root XML tag
:   `<ExpressionSetVersionVariableInput>`

JSON example
:   ```
              "variables": [
                {
                  "collection": false,
                  "dataType": "Text",
                  "decimalPlaces": 2,
                  "description": null,
                  "input": true,
                  "lookupName": "DM_for_test",
                  "lookupType": "DecisionMatrix",
                  "name": "City",
                  "objectName": null,
                  "output": false,
                  "resultStep": null,
                  "type": "Variable",
                  "value": null
                },
                {
                  "collection": false,
                  "dataType": "Text",
                  "decimalPlaces": null,
                  "description": null,
                  "input": false,
                  "lookupName": "DM_for_test",
                  "lookupType": "DecisionMatrix",
                  "name": "DM_for_test__State",
                  "objectName": null,
                  "output": true,
                  "resultStep": null,
                  "type": "Variable",
                  "value": null
                },
                {
                  "collection": false,
                  "dataType": "Text",
                  "decimalPlaces": null,
                  "description": "productName",
                  "input": true,
                  "lookupName": null,
                  "lookupType": null,
                  "name": "productName",
                  "objectName": null,
                  "output": false,
                  "resultStep": null,
                  "type": "Variable",
                  "value": null
                },
                {
                  "collection": false,
                  "dataType": "Boolean",
                  "decimalPlaces": null,
                  "description": "condition_output__1",
                  "input": false,
                  "lookupName": null,
                  "lookupType": null,
                  "name": "condition_output__1",
                  "objectName": null,
                  "output": true,
                  "resultStep": "Condition1",
                  "type": "Variable",
                  "value": null
                }
              ]
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `collection` | Boolean | Indicates whether the variable is a collection (`true`) or not (`false`). | Optional | 58.0 |
    | `data​Type` | String | Data type of the variable in an expression set version. Valid values are:   - `Action​Output` - `Boolean` - `Currency` - `Date` - `Date​Time` - `Decision​Matrix` - `Decision​Table` - `Numeric` - `Percent` - `Sobject` - `Sub​Expression` - `Text` | Required | 58.0 |
    | `decimal​Places` | Integer | Number of decimal places allowed for the value of the variable. | Optional | 58.0 |
    | `description` | String | Description of the variable. | Optional | 58.0 |
    | `input` | Boolean | Indicates whether the variable is an input of an expression set version (`true`) or not (`false`). | Optional | 58.0 |
    | `lookup​Name` | String | API name of the decision matrix, decision table, or subexpression. | Optional | 58.0 |
    | `lookup​Type` | String | Lookup type of the variable in an expression set version. Valid values are:   - `Decision​Matrix` - `Decision​Table` - `Sub​Expression` | Optional | 58.0 |
    | `name` | String | Name of the variable. | Required | 58.0 |
    | `object​Name` | String | Name of the object when the variable is of the sObject type. | Optional | 58.0 |
    | `output` | Boolean | Indicates whether the variable is output of an expression set version (`true`) or not (`false`). | Optional | 58.0 |
    | `result​Step` | String | Name of the step that’s assigning the value to this variable. | Optional | 58.0 |
    | `type` | String | Type of the variable in an expression set. Valid values are:   - `Constant` - `Formula` - `Variable` | Required | 58.0 |
    | `value` | String | Represents a value for a constant variable type and represents a formula for a formula variable type. | Optional | 58.0 |
