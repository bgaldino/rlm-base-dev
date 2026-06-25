---
page_id: connect_responses_expression_set_condition_criteria_output.htm
title: Expression Set Condition Criteria
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_expression_set_condition_criteria_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# Expression Set Condition Criteria

Output representation of a condition criteria in an expression
set.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Condition operator of the expression set. Valid values are:   - `Contains` - `DoesNotContain` - `Equals` - `GreaterThan​OrEquals` - `GreaterThan` - `IsNotNull` - `IsNull` - `LessThan` - `LessThan​OrEquals` - `NotEqualTo` | Small, 58.0 | 58.0 |
| `sequence​Number` | Integer | Sequence number of the condition in the advanced condition. | Small, 58.0 | 58.0 |
| `source​Field​Name` | String | Expression set version variable associated with the condition criteria. | Small, 58.0 | 58.0 |
| `value` | String | Value specified in the right-hand side of the condition. | Small, 58.0 | 58.0 |
| `value​Type` | String | Criteria value type of the expression set. Valid values are:   - `Formula` - `Literal` - `Parameter` | Small, 58.0 | 58.0 |
