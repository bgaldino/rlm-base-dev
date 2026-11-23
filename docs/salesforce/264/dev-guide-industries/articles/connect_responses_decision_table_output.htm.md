---
page_id: connect_responses_decision_table_output.htm
title: Decision Table Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-11-23
---

# Decision Table Output

Output representation of the decision table details.

JSON example for GET, POST, and PATCH
:   ```
    {
       "code":"200",
       "decisionTable":{
          "collectOperator":"Count",
          "conditionCriteria":"1 OR 2 OR 3",
          "conditionType":"Any",
          "decisionResultPolicy":"FirstMatch",
          "doesConsiderNullValue": true,
          "description":"Eligiblity of Products using Qualification Rules",
          "id":"0lDxx00000000BJ",
          "parameters":[
             {
                "fieldName":"IsDeleted",
                "isGroupByField":false,
                "isPriority":false,
                "operator":"Equals",
                "sequence":1,
                "usage":"Input"
             },
             {
                "fieldName":"CreatedById",
                "isGroupByField":false,
                "isPriority":false,
                "usage":"Output"
             },
             {
                "fieldName":"Title",
                "isGroupByField":false,
                "isPriority":false,
                "operator":"Equals",
                "sequence":3,
                "usage":"Input"
             },
             {
                "fieldName":"Id",
                "isGroupByField":false,
                "isPriority":false,
                "operator":"Equals",
                "sequence":2,
                "usage":"Input"
             }
          ],
          "setupName":"Product Qualification eligibility3",
          "sourceCriteria":[
             
          ],
          "sourceObject":"AccountFeed",
          "sourceType":"SingleSobject",
          "sourceconditionLogic":"1 AND 2 AND 3",
          "status":"Draft"
       },
       "isSuccess":true,
       "message":""
    }
    ```

JSON example for DELETE
:   ```
    {
       "code":"200",
       "isSuccess":true,
       "message":""
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Response code from the API request. | Small, 58.0 | 58.0 |
| `decisionTable` | [Decision Table Definition Output](./connect_responses_decision_table_definition_output.htm.md "Output representation of a decision table definition associated with a decision table.") | Details of the decision table definition associated with the decision table. | Small, 58.0 | 58.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 58.0 | 58.0 |
| `message` | String | Error message when the API request fails. | Small, 58.0 | 58.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
