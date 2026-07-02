---
page_id: connect_resources_decision_table_definition_details_post.htm
title: Decision Table Definitions (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_definition_details_post.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_table_resources.htm
fetched_at: 2026-06-25
---

# Decision Table Definitions (POST)

Create a decision table definition. A decision table definition
contains all the details required to create a decision table.

Resource
:   ```
    /connect/business-rules/decision-table/definitions
    ```

Resource Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/business-rules/decision-table/definitions
    ```

Available version
:   58.0

Requires Chatter
:   No

HTTP methods
:   POST

JSON example for a single object source
:   ```
    {
       "setupName":"Product Qualificiation eligibility",
       "fullName":"ProductQualificationEligibility",
       "description":"Eligiblity of Products using Qualification Rules",
       "usageType":"ProductEligibility",
       "sourceType":"SingleSobject",
       "sourceObject":"AccountFeed",
       "status":"Draft",
       "decisionResultPolicy":"FirstMatch",
       "doesConsiderNullValue": true,
       "collectOperator":"Count",
       "conditionType":"Any",
       "conditionCriteria":"1 OR 2 OR 3",
       "parameters":[
          {
             "fieldName":"IsDeleted",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"1"
          },
          {
             "fieldName":"Id",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"2"
          },
          {
             "fieldName":"Title",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"3"
          },
          {
             "fieldName":"CreatedById",
             "usage":"OUTPUT"
          }
       ]
    }
    ```

JSON example for a multi-object source
:   ```
    {
       "setupName":"Jumbo Pricing Definition",
       "fullName":"JumboPricingDefinition",
       "description":"Join all the DT definitions into one jumbo pricing definition",
       "usageType":"ProductEligibility",
       "type":"LowVolume",
       "sourceType":"MultipleSobjects",
       "sourceObject":"AccountFeed",
       "status":"Draft",
       "decisionResultPolicy":"OutputOrder",
       "doesConsiderNullValue": true,
       "collectOperator":"Count",
       "sourceconditionLogic":"1 AND 2 AND 3",
       "conditionType":"Any",
       "conditionCriteria":"1 OR 2 OR 3 OR 4 OR 5",
       "parameters":[
          {
             "fieldName":"IsDeleted",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"1",
             "columnMapping":"IsDeleted"
          },
          {
             "fieldName":"Id",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"2",
             "columnMapping":"Id"
          },
          {
             "fieldName":"Title",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"3",
             "columnMapping":"Title"
          },
          {
             "fieldName":"OldvalNumber",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"4",
             "columnMapping":"AccountHistory.OldvalNumber"
          },
          {
             "fieldName":"OldvalString",
             "usage":"INPUT",
             "operator":"Equals",
             "sequence":"5",
             "columnMapping":"AccountHistory.OldvalString"
          },
          {
             "fieldName":"CreatedById",
             "usage":"OUTPUT",
             "columnMapping":"CreatedById"
          },
          {
             "fieldName":"NewvalNumber",
             "usage":"OUTPUT",
             "columnMapping":"AccountHistory.NewvalNumber"
          },
          {
             "fieldName":"NewvalString",
             "usage":"OUTPUT",
             "columnMapping":"AccountHistory.NewvalString"
          }
       ]
       "sourceCriteria":[
          {
             "sourceFieldName":"OldvalString",
             "value":"5",
             "operator":"Equals",
             "valueType":"Parameter",
             "sequenceNumber":"1"
          }
       ]
    }
    ```

Request body for POST
:   Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `collectOperator` | String | Operator to apply a filter to outputs. Valid values are:  - `Count` - `Maximum` - `Minimum` - `None` - `Sum` | Optional | 58.0 |
        | `condition​Criteria` | String | Custom logic applied on the decision table columns to decide how the input fields are processed. | Optional Required when the condition type is `Custom`. | 58.0 |
        | `conditionType` | String | Condition logic for input fields. Valid values are:  - `All` - `Any` - `Custom` | Optional | 58.0 |
        | `description` | String | Description of the decision table. | Optional | 58.0 |
        | `decision​Result​Policy` | String | Results policy to filter results of the decision table. Valid values are:  - `AnyValue` - `CollectOperator—For   internal use only` - `FirstMatch` - `OutputOrder` - `Priority—For internal use   only` - `RuleOrder—For internal   use only` - `UniqueValues—For internal   use only` | Optional | 58.0 |
        | `doesConsider​NullValue` | Boolean | Indicates whether a column that has a null value is considered for lookup (`true`) or not (`false`). The default value is `false`. | Optional | 60.0 |
        | `fullName` | String | Unique name of the rule definition. | Required | 58.0 |
        | `isSet​Collect​Operator` | Boolean | For internal use only. Indicates whether the `collectOperator` is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Condition​Criteria` | Boolean | For internal use only. Indicates whether the `conditionCriteria` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Condition​Type` | Boolean | For internal use only. Indicates whether the `conditionType` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Description` | Boolean | For internal use only. Indicates whether the `description` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Decision​ResultPolicy` | Boolean | For internal use only. Indicates whether the `DecisionResultPolicy` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSetFullName` | Boolean | For internal use only. Indicates whether the `FullName` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSetParameters` | Boolean | For internal use only. Indicates whether the `parameters` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSetSetupName` | Boolean | For internal use only. Indicates whether the `setupName` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Source​conditionLogic` | Boolean | For internal use only. Indicates whether the `sourceConditionLogic` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Source​Criteria` | Boolean | For internal use only. Indicates whether the `sourceCriteria` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Source​Object` | Boolean | For internal use only. Indicates whether the `sourceObject` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSet​Source​Type` | Boolean | For internal use only. Indicates whether the `sourceType` is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSetType` | Boolean | For internal use only. Indicates whether the `type` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `isSetUsageType` | Boolean | For internal use only. Indicates whether the `UsageType` field is enabled (`true`) or not (`false`). | Optional | 58.0 |
        | `parameters` | [Decision Table Parameter Input](./connect_requests_decision_table_parameter_input.htm.md "Input representation of parameters defined for the decision table.")[] | Array of input and output fields for the decision table. | Optional | 58.0 |
        | `setupName` | String | Name of the decision table. | Required | 58.0 |
        | `source​condition​Logic` | String | Custom logic to filter the decision table rows. | Optional | 58.0 |
        | `sourceCriteria` | [Decision Table Source Criteria Input](./connect_requests_decision_table_source_criteria_input.htm.md "Input representation of source criteria for the decision table.")[] | Output array representation of source filters for the decision table rows, such as, `fieldName`, `operators`, `valueType`, and more. | Optional | 58.0 |
        | `sourceObject` | String | Object containing business rules for the decision table to read. | Required | 58.0 |
        | `sourceType` | String | Type of source to obtain decision table data. Valid values are:  - `CsvUpload` - `MultipleSobjects` - `SingleSobject` | Required | 58.0 |
        | `status` | String | Status of the decision table. Valid values are:  - `ActivationInProgress` - `ActivationInProgress` - `Draft` - `Inactive` | Required | 58.0 |
        | `type` | String | Type of the decision table. Valid values are:  - `HighVolume` - `LowVolume` | Optional | 58.0 |
        | `usageType` | String | Process type that uses the decision table. Valid values are:  - `Pricing` - `ProductEligibility` | Optional | 58.0 |

Response body for POST
:   [Decision Table Output](./connect_responses_decision_table_output.htm.md "Output representation of the decision table details.")
