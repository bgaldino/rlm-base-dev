---
page_id: connect_responses_decision_table_source_criteria_output.htm
title: Decision Table Source Criteria Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_source_criteria_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Source Criteria Output

Output representation of the decision table source
    criteria.

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

- 
- 
- 
- 
- 

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `operator` | String | Operator used in the filter criteria. Possible values are: `Contains` `DoesNotContain` `Equals` `GreaterThan` `GreaterThanOrEqual` `IsNotNull` `IsNull` `LessThan` `LessThanOrEqual` `NotEqual` | Small, 58.0 | 58.0 |
| `sequenceNumber` | Integer | Sequence number of the filter criteria in the associated decision table source condition. | Small, 58.0 | 58.0 |
| `sourceFieldName` | String | Name of the field in the filter criteria. | Small, 58.0 | 58.0 |
| `value` | String | Expected value of the field. | Small, 58.0 | 58.0 |
| `valueType` | String | Type of filter value. Possible values are: `Formula` `Literal` `Lookup` `Parameter` `PickList` | Small, 58.0 | 58.0 |
