---
article_id: ind.sf_contracts_relation_between_contract_status_and_obligation_state.htm
title: Relation Between Contract Status and Obligation State
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_relation_between_contract_status_and_obligation_state.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_obligation_management.htm
fetched_at: 2026-11-23
---

# Relation Between Contract Status and Obligation State

The default state of an obligation is On Hold. The state of the obligations associated with a contract is updated to Active, Inactive, or Expired based on any change in the contract's status and the start and end dates of the obligation.

The contract's impact on the obligation state is defined using the config value of the Activate Obligations Based on Contract Status contract type config setting. For example, if the config value is defined as Activated and:

The contract status doesn’t match the defined config value; then the default state of obligations associated with this contract is On Hold.

The contract status matches the defined config value; then the state of obligations associated with the contract is updated to Active, Inactive, or Expired based on the start and end dates of the obligation.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_relation_between_contract_status_and_obligation_state.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
