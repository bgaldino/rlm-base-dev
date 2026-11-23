---
page_id: lookup_tables_flow_metadata_api.htm
title: Flow for Lookup Tables
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/lookup_tables_flow_metadata_api.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_metadata_api_parent.htm
fetched_at: 2026-11-23
---

# Flow for Lookup Tables

Represents the metadata associated with a flow. With Flow, you can create an
application that navigates users through a series of screens to query and update records in the
database. You can also execute logic and provide branching capability based on user input to
build dynamic applications.

## FlowActionCall

Business Rules Engine exposes additional actionType values for the FlowActionCall Metadata
type. For more information on Flow and FlowActionCall metadata type, see [Flow](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_visual_workflow.htm).

### actionType

- **Field Type**: InvocableActionType (enumeration of type string)
- **Description**: Required. The action type. Additional valid values only for Lookup Tables include:
  - `runDecisionMatrix`—Invoke a
    decision matrix in a flow. This value is available in API version 55.0 and
    later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/lookup_tables_flow_metadata_api.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
