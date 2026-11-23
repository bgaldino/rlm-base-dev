---
page_id: connect_resources_contract_actions.htm
title: Contract Actions
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contract_actions.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-11-23
---

# Contract Actions

Execute possible actions for a contract based on the status. Actions can trigger work flows and change the status for a contract.

## Resource

```
/connect/clm/contract/$CONTRACT_ID
```

## Available Version

56.0

## HTTP Methods

PATCH

## Example for PATCH

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/clm/contract/${contractId}
```

## Request Body for PATCH

**JSON Example**

```
{
    "actionApiName" : "updateEnvelopeStatus",
...."actionId" : //object state action definition id,
    "actionData":{
        "isUpdateEnvelopeStatusSuccess": true
    }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `actionApiName` | String | API name for respective contract action. | Optional | 57.0 |
| `actionId` | String | ID for Object state Action Definition record. For the list of all standard actions supported, refer [Predefined Dynamic (Contract) Actions](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_Predefined_Contract_Actions.htm&type=5&language=en_US). | Optional | 57.0 |
| `actionData` | Map<String, String> | Action body with supported format string. | Optional | 57.0 |

![Note](/docs/resources/img/en-us/264.0?doc_id=images%2Ficon_note.png&folder=clm_developer_guide)

#### Note

For any request, either `actionApiName` or `actionId` must be passed. If none passed, the application raises an exception.

## Response Body for PATCH

[Generic Output Representation](./connect_responses_generic_output.htm.md "Generic output response.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contract_actions.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
