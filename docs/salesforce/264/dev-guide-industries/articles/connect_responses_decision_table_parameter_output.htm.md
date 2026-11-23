---
page_id: connect_responses_decision_table_parameter_output.htm
title: Decision Table Parameter Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_parameter_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-11-23
---

# Decision Table Parameter Output

Output representation of a decision table parameter.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `columnMapping` | String | Source object path for mapping to the column of an entity. | Small, 58.0 | 58.0 |
| `dataType` | String | Data type of the field used. Possible values are:  - `Boolean` - `Currency` - `Date` - `Number` - `Percent` - `String` | Small, 58.0 | 58.0 |
| `decimalScale` | Integer | Precision of the field used. | Small, 58.0 | 58.0 |
| `domainEntity` | String | Entity domain the field is mapped to. | Small, 58.0 | 58.0 |
| `fieldName` | String | Name of the field to be used in the decision table. | Small, 58.0 | 58.0 |
| `isGroupByField` | Boolean | Indicates whether the field is used to group the business rules of the decision table (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `isPriority` | Boolean | Indicates whether it is a priority field (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `maxlength` | Integer | Maximum length of the field used. | Small, 58.0 | 58.0 |
| `operator` | String | Valid operators for a field based on its usage. Possible values are:  - `Between` - `DoesNotExistIn` - `Equals` - `ExistsIn` - `GreaterOrEqual` - `GreaterThan` - `LessOrEqual` - `LessThan` - `Matches` - `NotEquals` | Small, 58.0 | 58.0 |
| `sequence` | Integer | Sequence in which input fields are processed. | Small, 58.0 | 58.0 |
| `sortType` | String | Type of sorting done on the rows of a decision table. Possible values are:  - `AscNullFirst` - `AscNullLast` - `DescNullFirst` - `DescNullLast` - `None` | Small, 58.0 | 58.0 |
| `usage` | String | Usage type for a field. Possible values are:  - `Input` - `Output` | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_parameter_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
