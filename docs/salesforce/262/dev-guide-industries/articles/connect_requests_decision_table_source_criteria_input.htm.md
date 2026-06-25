---
page_id: connect_requests_decision_table_source_criteria_input.htm
title: Decision Table Source Criteria Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_table_source_criteria_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_requests.htm
fetched_at: 2026-06-25
---

# Decision Table Source Criteria Input

Input representation of source criteria for the decision
table.

Root XML tag

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `operator` | String | Operator used in the filter criteria. Possible values are:  - `Contains` - `DoesNotContain` - `Equals` - `GreaterThan` - `GreaterThanOrEqual` - `IsNotNull` - `IsNull` - `LessThan` - `LessThanOrEqual` - `NotEqual` | Required | 58.0 |
    | `sequenceNumber` | Integer | Sequence number of the filter criteria in the associated decision table source condition. | Optional | 58.0 |
    | `sourceFieldName` | String | Name of the field in the filter criteria. | Required | 58.0 |
    | `value` | String | Expected value of the field. | Optional | 58.0 |
    | `valueType` | String | Type of a filter value. Possible values are:  - `Formula` - `Literal` - `Lookup` - `Parameter` - `PickList` | Required | 58.0 |
