---
article_id: ind.sf_contracts_sample_workflows_to_create_and_customize_contract_object_state_definitions.htm
title: Sample Workflows to Create and Customize Contract Object State Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_sample_workflows_to_create_and_customize_contract_object_state_definitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Sample Workflows to Create and Customize Contract Object State Definitions

You can customize or create contract Object State Definitions as per your business needs. This sections details few sample customizations.

Workflow to Remove Contract Status Values From A Contract Object State Definition
You can edit the picklist values of a record type to include only certain states for a contract. For example, you can remove record type values that are specific to e-signature.
Workflow to Create a New Contract Object State Definition and Map it to a New Record Type
You can create a new Object State Definition with specific Object State Values and Object State Transitions. Then create a record type and edit the picklist values of a record type to include only certain states for a contract. When you create a contract, the contract states only includes states that you kept in the record type status.
Workflow to Configure New Contract Status Values and Map To Contract Object State Definition
You can configure a customized Object State Definition for your users by adding new contract status values and mapping it to an existing contract Object State Definition.
Workflow to Create a Custom Object State Action Definition
You can create an Object State Definition (state model) with specific Object State Values and Object State Transitions. In the Object State Definition, you can define custom actions that call specific transitions using an Apex Class or Omniscript.
