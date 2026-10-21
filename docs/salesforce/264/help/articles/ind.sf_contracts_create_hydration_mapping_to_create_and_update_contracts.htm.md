---
article_id: ind.sf_contracts_create_hydration_mapping_to_create_and_update_contracts.htm
title: Create Hydration Mapping to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_hydration_mapping_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_map_context_definitions_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Create Hydration Mapping to Create and Update Contracts

Data is first fetched from objects through hydration mapping and then temporarily stored in the cache. Within the node, separate structures such as contract cache and sales contract line cache store relevant data such as attribute name, type, and data type.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create hydration mapping:	

Context Service Admin

After you create your context definition, search for objects and click the node and attribute icons that you want to connect to the object fields to start mapping.

From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
Select the context definition that you want to add a mapping to.
On the Context Definition Details page, go to the Map Data tab.
Click Add Mapping.
Specify the mapping details for hydration mapping.
Give your mapping a name.
For example, AssestToCntrlHydrationMapping.
Provide a description. Enter additional details about the context mapping, if necessary.
To enable the method to satisfy the ContractCache conditions: the IsAssociatedWithClm flag is selected, and the contract status is set to draft, select Automatic Salesforce object mapping.
To set this mapping as your default mapping, select Mark as Default.
At least one hydration mapping must be set as default under each context definition.
Click Next.
To determine the mapping type, select Hydration and Translation as mapping intent.
To begin mapping, click Map.
You’re directed to Context Mapping’s builder page to begin mapping your nodes and attributes.
To continue mapping, refer to the steps in the Add Context Mapping topic.
After you define your context definition, its structure, and its mapping, activate it. Salesforce Contracts can now use the context definition to perform application processes with improved performance.

See Also

Add Context Mapping

Activate Context Definition
