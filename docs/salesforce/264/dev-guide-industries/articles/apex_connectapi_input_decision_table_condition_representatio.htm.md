---
page_id: apex_connectapi_input_decision_table_condition_representatio.htm
title: ConnectApi.DecisionTableCondition
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table_condition_representatio.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apex_input_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.DecisionTableCondition

Input representation of the decision table condition.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fieldName` | String | The field name that is selected as an input for the decision table. | Required | 51.0 |
| `operator` | String | The operator used for the input field. Valid values are:  - `DoesNotExistIn`—Use to check if the   input value doesn’t exist in a multi-select picklist. - `Equals`—Use to check if the input value   equals to the configured value in the rule. - `ExistsIn`—Use to check if the input   value exists in a multi-select picklist. - `GreaterOrEqual`—Use to check if the   input value is greater than or equal to the configured value in the rule. - `GreaterThan`—Use to check if the input   value is greater than the configured value in the rule. - `LessOrEqual`—Use to check if the input   value is less than or equal to the configured value in the rule. - `LessThan`—Use to check if the input   value is less than the configured value in the rule. - `Matches`—Use to check if the input value   is a substring of the value in the rule. - `NotEquals`—  The operator specified here overrides the operator defined in Decision Table. | Optional | 51.0 |
| `sourceObject` | String | The name of source object for the input field. The source object field is not mandatory if the dataset link is configured with a single source object. The source object field is required only when the dataset link definition contains multiple source objects. | Optional | 52.0 |
| `value` | Object | The value of the data type that is selected as an input. | Required | 51.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/apex_connectapi_input_decision_table_condition_representatio.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
