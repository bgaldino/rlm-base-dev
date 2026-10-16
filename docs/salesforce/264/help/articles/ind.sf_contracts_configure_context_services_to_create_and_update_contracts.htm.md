---
article_id: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
title: Configure Context Service to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_create_contract_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Configure Context Service to Create and Update Contracts

Context Service provides a mapping interface for creating and updating contracts from standard and custom objects. Context Service replaces the XML field mapping framework with a configurable, point-and-click approach.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

Turn on the context service settings to use the out-of-the-box ContractsContextDefinition mapping. You can also configure the use case-specific context definitions to create and update contracts from objects. Salesforce Contracts supports the export and import of context use case mapping to create and update contracts.

IMPORTANT Salesforce Contracts recommends that you use the Context Service framework to create and update contracts from objects.
See Also

Context Service

Learn and Explore Context Service

Context Service Limits

Enable Context Service for Salesforce Contracts
Turn on Context Service for Salesforce Contracts to switch the create and update contract APIs from the XML field mapping framework to the Context Service framework.
Context Definitions to Create and Update Contracts
A context definition defines the relationship between nodes and attributes to access data from a mapped source. Use the predefined ContractsContextDefinition to create and update contracts from an Opportunity, Quote, or Order, or create a custom definition.
Custom Context Definitions to Create and Update Contracts
Create a custom context definition by choosing nodes, defining their relationship, and adding attributes. These custom definitions are available on the Custom Definitions tab. You can create custom definitions by using the new, extend, and clone actions.
Map Context Definitions to Create and Update Contracts
After you create a context definition, define where data is fetched from by creating hydration and persistence mappings at both the node and attribute levels. Map nodes and attributes to the appropriate object fields to ensure accurate data input.
Context Use Case Mapping to Create and Update Contracts
Context Use Case Mapping stores the configuration that defines how the context service creates and updates contracts from any object. Default mappings for Opportunity, Order, and Quote are available under ContractsContextDefinitions, and admins can configure additional use case-specific context definitions.
