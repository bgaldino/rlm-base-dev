---
article_id: ind.sf_contracts_view_the_standard_contractscontextdefinition_mapping.htm
title: View the Standard ContractsContextDefinition Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_view_the_standard_contractscontextdefinition_mapping.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_context_definitions_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# View the Standard ContractsContextDefinition Mapping

After you turn on the Context Service for Salesforce Contracts setting, the default ContractsContextDefinition mapping is available. Use the predefined definition to create and update contracts. The definition includes six mappings: three hydration and three persistence mappings for the Opportunity, Order, and Quote standard objects.

IMPORTANT You can’t edit or delete a standard context definition that’s shipped with Salesforce Contracts. You can extend or clone it and make your modifications.
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To view context definitions:	

Context Service Run Time User

From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
To view the predefined context definitions, go to the Standard Definitions tab.
Click ContractsContextDefinition.
To view the nodes and associated attributes, go to the Structure tab.
To view the mappings, go to the Map Data tab.
The map data has six mappings, one each for hydration and persistence for the Opportunity, Order, and Quote standard Salesforce objects.
To view the mapping details, click the down arrow next to the mapping source name, and select View sObject Mapping.
For example, OppToCntrHydrationMapping shows the mapping of fields from the Opportunity object to the corresponding fields in the cache.
To view the mapping details, click the down arrow next to the mapping source, and select View Input Mapping.
The ContractCache is the parent node, and SalesContractLineCache is the child node.

See Also

View, Edit, and Delete Saved Context Definitions
