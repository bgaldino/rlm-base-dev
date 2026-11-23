---
article_id: ind.sf_contracts_create_custom_context_definitions_to_create_and_update_contracts.htm
title: Create Custom Context Definitions to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_custom_context_definitions_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_custom_context_definitions_to_create_and_update_contracts.htm
fetched_at: 2026-11-23
---

# Create Custom Context Definitions to Create and Update Contracts

Create a context definition by choosing nodes, defining their relationship, adding attributes, and applying context tags. To create and update contracts, the Contract admin must ensure that the parent node has these required attributes configured: Account, IsAssociatedWithClm, Status, and the custom source field ID, and that the child node has the ContractId configured.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create custom context definitions:	

Context Service Admin

Create Context Definitions.
Follow the steps in the create context definitions topic.
Add three mandatory attributes to the parent node by choosing an input type, the data type, and value if you have a key-value pair.
Click Add Attributes.
Specify these attribute details.

Attribute Name: Status, Type: OUTPUT, Data Type: Picklist

Attribute Name: IsAssociatedWithClm, Type: OUTPUT, Data Type: Boolean

Attribute Name: <source field ID>, Type: OUTPUT, Data Type: String

For example, SourceAssetId. It isn't mandatory to add the word 'source" as a prefix to the custom field. The custom field name must match the Contract, Contract Use Case Mapping, and Context Definition Mapping node structure.
Add the contract ID attribute to the child node by choosing an input type, the data type, and value if you have a key-value pair.
Click Add Attributes.
Specify these attribute details.

Attribute Name: ContractId

Type: INPUT OUTPUT

Data Type: String

See Also

Create Context Definitions

Create Custom Source Field For Contract Object

View 'Is Associated With CLM'

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_custom_context_definitions_to_create_and_update_contracts.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
