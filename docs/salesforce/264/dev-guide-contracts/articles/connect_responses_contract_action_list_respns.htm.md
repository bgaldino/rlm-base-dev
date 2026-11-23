---
page_id: connect_responses_contract_action_list_respns.htm
title: Contract Action List
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_action_list_respns.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_apis_responses.htm
fetched_at: 2026-11-23
---

# Contract Action List

List of contract actions.

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actions` | [Contract Action[]](./connect_responses_contract_action_respons.htm.md "Contract action response for a particular contract ID.") | Specifies list of actions. | Big, 56.0 | 56.0 |
| `contractId` | String | Indicates ID of the contract. | Small, 56.0 | 56.0 |

## JSON Example

```
{
    "actions": [
        {
            "apiName": "cancelContract",
            "uiText": "Cancel Contract"
        },
        {
            "apiName": "submitForApproval",
            "uiText": "Submit for Approval"
        }
    ],
    "contractId": "800RO000000U7FaYAK"
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_responses_contract_action_list_respns.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
