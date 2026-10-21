---
article_id: ind.sf_contracts_create_persistence_mapping_to_create_and_update_contracts.htm
title: Create Persistence Mapping to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_persistence_mapping_to_create_and_update_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_map_context_definitions_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Create Persistence Mapping to Create and Update Contracts

Persistence mapping specifies how data from one object, such as an opportunity or account, is persisted or saved into another object, such as a contract. It defines the relationship between the fields in different objects. Persistence mapping ensures data is correctly synced and updated across the Salesforce environment during the create and update contract actions.

For example, using persistence mapping, the CLM admin can specify that when an opportunity is created, certain fields from that opportunity are copied into the corresponding fields in a contract object. For example, the opportunity name, amount, and close date. Persistence mapping ensures that information related to the opportunity is accurately reflected in the contract record. Configure persistence mappings to handle various scenarios, such as creating records, updating records, or syncing data between related objects. They play a crucial role in maintaining data integrity and consistency within Salesforce contracts and associated objects.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create a persistence mapping:	

Context Service Admin

After you create your context definition, search for objects and click the node and attribute icons that you want to connect to the object fields to start mapping.

From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
Select the context definition that you want to add a mapping to.
On the Context Definition Details page, go to the Map Data tab.
Click Add Mapping.
Specify the mapping details for persistence mapping.
Give your mapping a name.
For example, AssestToCntrlPersistenceMapping.
Provide a description. Enter additional details about the context mapping, if necessary.
To set this mapping as your default mapping, select Mark as Default.
Click Next.
To determine the mapping type, select Hydration, Persistence, and Translation as mapping intent and supported mapping.
To begin mapping, click Map.
You’re directed to Context Mapping’s builder page to begin mapping your nodes and attributes.
To continue mapping, refer to the steps in the Add Context Mapping topic.
After you define your context definition, its structure, and its mapping, activate it. Salesforce Contracts can now use the context definition to perform application processes with improved performance.

See Also

Add Context Mapping
