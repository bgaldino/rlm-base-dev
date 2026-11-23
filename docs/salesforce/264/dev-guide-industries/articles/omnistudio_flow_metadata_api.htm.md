---
page_id: omnistudio_flow_metadata_api.htm
title: Flow for Omnistudio
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/omnistudio_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# Flow for Omnistudio

Represents the metadata associated with a flow. Use a flow to create an application
that takes users through a series of pages to query and update records in the database. You can
also execute logic and provide branching capability based on user input to build dynamic
applications.

## FlowActionCall

Omnistudio exposes additional actionType values for the FlowActionCall Metadata type.

### actionType

- **Field Type**: InvocableActionType (enumeration of type string)
- **Description**: Required.

  The action type. Additional valid value only for Omnistudio include:

  - `executeIntegrationProcedure`—Executes an Integration Procedure
    with Agentforce configured. Available in API version 64.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/omnistudio_flow_metadata_api.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
