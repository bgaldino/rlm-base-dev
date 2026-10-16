---
article_id: ind.sf_contracts_custom_context_definitions_to_create_and_update_contracts.htm
title: Custom Context Definitions to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_custom_context_definitions_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Custom Context Definitions to Create and Update Contracts

Create a custom context definition by choosing nodes, defining their relationship, and adding attributes. These custom definitions are available on the Custom Definitions tab. You can create custom definitions by using the new, extend, and clone actions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

To create context definitions within Salesforce Contracts, follow this sequence:

Create, clone, or extend a custom context definition.
Define hydration and persistence mappings for your objects.
Map context definitions.

After you create a context definition, define where the data is fetched from. Mapping data must be fetched from a data source for both the node and the attribute levels of the context definition.

Create custom use case mapping.
Activate the context definition so that the definition is available in the context definition name dropdown when you create your context use case mapping.
NOTE If you aren't familiar with Context Service and Context Definitions, see the Context Definitions documentation.
Create Custom Context Definitions to Create and Update Contracts
Create a context definition by choosing nodes, defining their relationship, adding attributes, and applying context tags. To create and update contracts, the Contract admin must ensure that the parent node has these required attributes configured: Account, IsAssociatedWithClm, Status, and the custom source field ID, and that the child node has the ContractId configured.
