---
page_id: expression-set-flow-metadata-api
title: Flow for Expression Set
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/expression-set-flow-metadata-api.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: expression-set-metadata-api-parent
legacy_page_id: expression_set_flow_metadata_api.htm
fetched_at: 2026-11-25
---

# Flow for Expression Set

Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Business Rules Engine exposes additional actionType values for the FlowActionCall Metadata type. For more information on Flow and FlowActionCall metadata type, see [Flow](https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_visual_workflow.htm).

### actionType

- 

**Field Type**: InvocableActionType (enumeration of type string)

- 

**Description**: Required. The action type. Additional valid values only for Expression Set include:

  - `runExpressionSet`—Invoke an active expression set. This value is available in API version 55.0 and later.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/expression-set-flow-metadata-api.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
