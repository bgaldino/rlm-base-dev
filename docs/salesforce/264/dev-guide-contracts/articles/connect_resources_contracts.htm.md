---
page_id: connect_resources_contracts.htm
title: Contracts (PATCH, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contracts.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clm_resources.htm
fetched_at: 2026-11-23
---

# Contracts (PATCH, POST)

Update and create contracts using the object ID.

## Resource

```
/connect/clm/contract
```

## Available Version

56.0

## HTTP Methods

PATCH, POST

## Example for PATCH

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract
```

## Example for POST

```
https://YOUR_INSTANCE.salesforce.com/services/data/v56.0/connect/clm/contract
```

## Request Body

**JSON Example for Creating and Updating Contract**

```
{
"sourceObjectId" : "006xx000001a4KaAAI",
"templateName" : "Value1",
"isAutoDocgenRequired" :true/false
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isAutoDocgenRequired` | Boolean | Specifies whether automatic document generation is required or not. | Required | 56.0 |
| `recordTypeName` | String | Contract record type name. | Optional | 56.0 |
| `sourceObjectId` | String | Source record ID. | Required | 56.0 |
| `templateName` | String | Document template name for document generation. | Optional | 56.0 |

## Response Body

[Contract Output Response Representation](./connect_responses_contract_output_response.htm.md "Contract list.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_contracts.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
