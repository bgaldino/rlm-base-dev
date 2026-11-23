---
page_id: clm_flow_metadata_api.htm
title: Flow for Salesforce Contracts
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/clm_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: clm_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# Flow for Salesforce Contracts

Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Salesforce Contracts exposes additional actionType values for the FlowActionCall Metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Salesforce Contracts includes `searchContractDocument`—Search the latest contract document version based on the user's query. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/clm_flow_metadata_api.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
