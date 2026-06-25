---
page_id: connect_responses_decision_table_definition_output.htm
title: Decision Table Definition Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_definition_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-06-25
---

# Decision Table Definition Output

Output representation of a decision table definition associated with a
decision table.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `collectOperator` | String | Operator applied to outputs. Valid values are:  - `Count` - `Maximum` - `Minimum` - `None` - `Sum` | Small, 58.0 | 58.0 |
| `conditionCriteria` | String | Custom logic for deciding how the input fields are processed. | Small, 58.0 | 58.0 |
| `conditionType` | String | Condition logic for input fields. Valid values are:  - `All` - `Any` - `Custom` | Small, 58.0 | 58.0 |
| `decision​Result​Policy` | String | Results policy to specify the result of the decision table. Valid values are:  - `AnyValue` - `CollectOperator—For   internal use only` - `FirstMatch` - `OutputOrder` - `Priority—For internal use   only` - `RuleOrder—For internal   use only` - `UniqueValues—For internal   use only` | Small, 58.0 | 58.0 |
| `description` | String | Description of the decision table. | Small, 58.0 | 58.0 |
| `doesConsider​NullValue` | Boolean | Indicates whether a column that has a null value is considered for lookup (`true`) or not (`false`). The default value is `false`. | Small, 60.0 | 60.0 |
| `fullName` | String | Unique name of the rule definition. | Small, 58.0 | 58.0 |
| `id` | String | ID of the decision table. | Small, 58.0 | 58.0 |
| `parameters` | [Decision Table Parameter Output](./connect_responses_decision_table_parameter_output.htm.md "Output representation of a decision table parameter.")[] | Array of input fields defined for the decision table. | Small, 58.0 | 58.0 |
| `setupName` | String | Name of the decision table. | Small, 58.0 | 58.0 |
| `sourceCriteria` | [Decision Table Source Criteria Output](./connect_responses_decision_table_source_criteria_output.htm.md "Output representation of the decision table source criteria.")[] | Output array representation of source filters. | Small, 58.0 | 58.0 |
| `sourceObject` | String | Object containing business rules for the decision table to read. | Small, 58.0 | 58.0 |
| `sourceType` | String | Type of source used to obtain decision table data. Valid values are:  - `CsvUpload` - `MultipleSobjects` - `SingleSobject` | Small, 58.0 | 58.0 |
| `sourceconditionLogic` | String | Custom logic for deciding how criteria on source is applied. | Small, 58.0 | 58.0 |
| `status` | String | Status of the decision table. Valid values are:  - `ActivationInProgress` - `ActivationInProgress` - `Draft` - `Inactive` | Small, 58.0 | 58.0 |
| `usageType` | String | Process type that uses the decision table. Valid values are:  - `Pricing` - `ProductEligibility` | Small, 58.0 | 58.0 |
