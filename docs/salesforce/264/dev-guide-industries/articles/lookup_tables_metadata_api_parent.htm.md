---
page_id: lookup_tables_metadata_api_parent.htm
title: Lookup Tables Metadata API Types
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/lookup_tables_metadata_api_parent.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_parent.htm
fetched_at: 2026-11-23
---

# Lookup Tables Metadata API Types

Metadata API enables you to access some types and feature settings that you can
customize in the user interface.

The following list links to reference information for these metadata types.

- [DecisionMatrixDefinition](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_decisionmatrixdefinition.htm)

  Represents a definition of a decision matrix.
- [Flow](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_visual_workflow.htm)

  Represents the metadata associated with a flow that encompasses the flow's structure, logic, and run-time behavior.

  - [Flow for Lookup Tables](./lookup_tables_flow_metadata_api.htm.md "Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.")

    Business Rules Engine exposes additional actionType values for the FlowActionCall Metadata type.
- [DecisionTable](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_decisiontable.htm)

  Represents the information about a decision table.
- [DecisionTableDatasetLink](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_decisiontabledatasetlink.htm)

  Represents the information about a dataset link associated with a decision table. In a dataset link, select an object for whose records, the decision table must provide an outcome. This type extends the Metadata metadata type and inherits its fullName field.

#### See Also

- [*Metadata API Developer Guide*: Understanding Metadata API](https://developer.salesforce.com/docs/atlas.en-us.264.0.api_meta.meta/api_meta/meta_intro.htm "Metadata API Developer Guide: Understanding Metadata API - HTML (New Window)")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/lookup_tables_metadata_api_parent.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
