---
page_id: product-configurator-flow-metadata-api
title: Flow for Product Configurator
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-flow-metadata-api.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-metadata-api-parent
legacy_page_id: product_configurator_flow_metadata_api.htm
fetched_at: 2026-11-25
---

# Flow for Product Configurator

Represents the metadata associated with a flow. With Flow, you can create an application that navigates users through a series of screens to query and update records in the database. You can also execute logic and provide branching capability based on user input to build dynamic applications.

## FlowActionCall

Product Configurator exposes additional actionType values for the FlowActionCall Metadata type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| `actionType` | InvocableActionType (enumeration of type string) | Required. The action type. Additional valid values only for Product Configurator include `runConfigRules`—Run rules for a specific quote or order based on a context ID or transaction ID, and process other steps that are part of the configuration directly within a Flow. This action decouples rule execution from configurations to enable independent execution of rules and for easier retrieval of responses. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/product-configurator-flow-metadata-api.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
