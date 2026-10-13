---
article_id: ind.sf_contracts_map_context_definitions_to_create_and_update_contracts.htm
title: Map Context Definitions to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_map_context_definitions_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_context_services_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Map Context Definitions to Create and Update Contracts

After you create a context definition, define where data is fetched from by creating hydration and persistence mappings at both the node and attribute levels. Map nodes and attributes to the appropriate object fields to ensure accurate data input.

Important:

Salesforce recommends that you create a context definition, define its structure, set its mapping, and only then make the context definition active.

To make a context definition active, you must set up any hydration mapping as a default mapping.

You must map the nodes first and then map all attributes.

To save a context map, map at least one attribute and a node.

The Profile, UserRole, RecordType, URL, and Permission Set Assignment entities aren’t available for mapping.

See Also

Mapping Types

View and Edit Saved Context Mapping

Add Context Mapping

Create Hydration Mapping to Create and Update Contracts
Data is first fetched from objects through hydration mapping and then temporarily stored in the cache. Within the node, separate structures such as contract cache and sales contract line cache store relevant data such as attribute name, type, and data type.
Create Persistence Mapping to Create and Update Contracts
Persistence mapping specifies how data from one object, such as an opportunity or account, is persisted or saved into another object, such as a contract. It defines the relationship between the fields in different objects. Persistence mapping ensures data is correctly synced and updated across the Salesforce environment during the create and update contract actions.
