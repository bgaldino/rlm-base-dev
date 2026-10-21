---
article_id: ind.sf_contracts_configure_context_use_case_mapping_for_contracts.htm
title: Configure Context Use Case Mapping to Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configure_context_use_case_mapping_for_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_context_use_case_mapping_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Configure Context Use Case Mapping to Create and Update Contracts

Context Use Case Mapping is the setup entity that stores the configuration details for the context service for Salesforce Contracts. It specifies the definition and mapping to be consumed to create and update contracts from any object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

Contract admins can further customize context definitions tailored to specific use cases to create and update contracts from objects. For example, you can define a specific combination to create a contract from the Asset object. The combination includes the record type, source object field for Asset in Contract, contract context definition, hydration and persistence mapping type, and mapping name. The use case type is always Create Contract or Update Contract.

USER PERMISSIONS NEEDED	 
To create a persistence mapping:	

Context Service Admin

Important: For the Create Contract and Update Contract actions to work seamlessly, ensure consistency in the usage of target object custom field name.

To map the object fields with the Contract fields, the custom field name must be a valid custom field name in the Contract object.

To configure the context definition, use the API name of the same custom field to add an attribute to the node structure.

Map the custom field in the persistence mapping. When the Mapping Type is set to Persistence, the defined Target Object Custom Field Name is used to persist the data from the cache to the Contract object. This field isn’t applicable to hydration mapping.

NOTE In Summer ‘24, you can use only the predefined Create Contract or Update Contract use case type.
From Setup, in the Quick Find box, enter Contract Lifecycle Management, and then select Context Use Case Mapping.
Click New.
Enter these details:
Reference Object Name: Enter the reference object name.
Reference Object Record Type: Select a reference object record type.
Target Object Name: Enter Contract.
Target Object Record Type: Select a target object reference type.
Target Object Custom Field Name: Enter a valid custom field name that is in the Contract object.
Context Definition Name: Select a context definition name.
Mapping Type: Select Hydration or Persistence.
Mapping Name: Select a mapping name.
Use Case Type: Select Create Contract or Update Contract.
Save your changes.
