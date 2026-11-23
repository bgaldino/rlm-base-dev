---
article_id: ind.sf_contracts_context_use_case_mapping_to_create_and_update_contracts.htm
title: Context Use Case Mapping to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_context_use_case_mapping_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
fetched_at: 2026-11-23
---

# Context Use Case Mapping to Create and Update Contracts

Context Use Case Mapping stores the configuration that defines how the context service creates and updates contracts from any object. Default mappings for Opportunity, Order, and Quote are available under ContractsContextDefinitions, and admins can configure additional use case-specific context definitions.

Create Contract: When you create a contract, the mapping used from the Context Use Case Mapping object is based on the target object record type selected to create the contract. The app searches the Context Use Case Mapping object for the selected record type and consumes the associated hydration and persistence mapping.

Update Contract: When you update contracts, the contract's target object record type isn’t considered. All the contracts associated with the reference object are updated.

IMPORTANT To ensure that the update contract action seamlessly integrates with the intended context definition, the Context Use Case Mapping must contain at least one hydration and persistence mapping, with the Target Object Record Type field set to null.
Configure Context Use Case Mapping to Create and Update Contracts
Context Use Case Mapping is the setup entity that stores the configuration details for the context service for Salesforce Contracts. It specifies the definition and mapping to be consumed to create and update contracts from any object.
Use Case Mapping Parameters To Create and Update Contracts
The Context Use Case Mapping is the setup entity that stores the configuration details for the context service for Salesforce Contracts.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_context_use_case_mapping_to_create_and_update_contracts.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
