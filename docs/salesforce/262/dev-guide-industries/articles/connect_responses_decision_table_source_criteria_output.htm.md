---
page_id: connect_responses_decision_table_source_criteria_output.htm
title: Decision Table Source Criteria Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_source_criteria_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-06-25
---

# Decision Table Source Criteria Output

Output representation of the decision table source
criteria.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Operator used in the filter criteria. Possible values are:  - `Contains` - `DoesNotContain` - `Equals` - `GreaterThan` - `GreaterThanOrEqual` - `IsNotNull` - `IsNull` - `LessThan` - `LessThanOrEqual` - `NotEqual` | Small, 58.0 | 58.0 |
| `sequenceNumber` | Integer | Sequence number of the filter criteria in the associated decision table source condition. | Small, 58.0 | 58.0 |
| `sourceFieldName` | String | Name of the field in the filter criteria. | Small, 58.0 | 58.0 |
| `value` | String | Expected value of the field. | Small, 58.0 | 58.0 |
| `valueType` | String | Type of filter value. Possible values are:  - `Formula` - `Literal` - `Lookup` - `Parameter` - `PickList` | Small, 58.0 | 58.0 |
