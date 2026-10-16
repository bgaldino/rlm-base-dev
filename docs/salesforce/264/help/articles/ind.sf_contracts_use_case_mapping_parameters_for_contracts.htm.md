---
article_id: ind.sf_contracts_use_case_mapping_parameters_for_contracts.htm
title: Use Case Mapping Parameters To Create and Update Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_use_case_mapping_parameters_for_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_context_use_case_mapping_to_create_and_update_contracts.htm
fetched_at: 2026-10-13
---

# Use Case Mapping Parameters To Create and Update Contracts

The Context Use Case Mapping is the setup entity that stores the configuration details for the context service for Salesforce Contracts.

List of the use case mapping parameters and their descriptions.

FIELD	DESCRIPTION
Reference Object Name	The standard or custom source object that the context mapping is fetched from.
Reference Object Record Type	The record types that are associated with the reference object.
Target Object Name	The name of the standard or custom object that the context mapping from the reference object is pushed to.
Target Object Record Type	The record types that are associated with the Contract object.
Target Object Custom Field Name	The name of the custom field in the target object that's used to link the target object with the reference object. The custom field must be a valid field in the Contract object.
Context Definition Name	The name of the context definition that stores the hydration and persistence mapping details. The dropdown lists all active context definitions.
Mapping Type	Specifies the mapping type used for the context use case mappings, such as hydration and persistence. The dropdown lists the mapping types associated with the selected context definition name.
Mapping Name	The name of the mapping that's associated with the MappingType. For example, OppToCntrHydrationMapping and OppToCntrPersistenceMapping.
Use Case Type	Specifies the usage that the context definition and mapping are defined for. Select Create Contract or Update Contract.
