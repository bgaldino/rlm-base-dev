---
article_id: ind.sf_contracts_context_definitions_to_create_and_update_contracts.htm
title: Context Definitions to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_context_definitions_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Context Definitions to Create and Update Contracts

A context definition defines the relationship between nodes and attributes to access data from a mapped source. Use the predefined ContractsContextDefinition to create and update contracts from an Opportunity, Quote, or Order, or create a custom definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
See Also

View, Edit, and Delete Saved Context Definitions

Extend Context Definition

View the Standard ContractsContextDefinition Mapping
After you turn on the Context Service for Salesforce Contracts setting, the default ContractsContextDefinition mapping is available. Use the predefined definition to create and update contracts. The definition includes six mappings: three hydration and three persistence mappings for the Opportunity, Order, and Quote standard objects.
ContractCache and SalesContractLineCache Nodes
Nodes are canonical objects containing the attributes mapped to real data by the consuming application. A structure is defined between the nodes to ensure that the right set of information is passed during each step of the process.
