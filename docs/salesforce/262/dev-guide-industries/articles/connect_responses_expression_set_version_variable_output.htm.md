---
page_id: connect_responses_expression_set_version_variable_output.htm
title: Expression Set Version Variable
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_version_variable_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# Expression Set Version Variable

Output representation of a variable in an expression set
version.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `collection` | Boolean | Indicates whether the variable is a collection (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `data​Type` | String | Variable data type for the expression set.  - `Action​Output` - `Boolean` - `Currency` - `Date` - `Date​Time` - `Decision​Matrix` - `Decision​Table` - `Numeric` - `Percent` - `Sobject` - `Sub​Expression` - `Text` | Small, 58.0 | 58.0 |
| `decimal​Places` | Integer | Number of decimal places allowed for the value of the variable. | Small, 58.0 | 58.0 |
| `description` | String | Description of the variable. | Small, 58.0 | 58.0 |
| `input` | Boolean | Indicates whether the variable is the input of an expression set version (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `lookup​Name` | String | API name of the decision matrix, decision table, or subexpression. | Small, 58.0 | 58.0 |
| `lookup​Type` | String | Variable lookup type of the expression set. Valid values are:   - `Decision​Matrix` - `Decision​Table` - `Sub​Expression` | Small, 58.0 | 58.0 |
| `name` | String | Name of the variable. | Small, 58.0 | 58.0 |
| `object​Name` | String | Name of the object when the variable is of sObject type. | Small, 58.0 | 58.0 |
| `output` | Boolean | Indicates whether the variable is the output of an expression set version (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `result​Step` | String | Name of the step that’s producing the value to the variable. | Small, 58.0 | 58.0 |
| `type` | String | Variable type of the expression set. Valid values are:   - `Constant` - `Formula` - `Variable` | Small, 58.0 | 58.0 |
| `value` | String | Represents a value in case of a constant variable type and a formula in case of a formula variable type. | Small, 58.0 | 58.0 |
