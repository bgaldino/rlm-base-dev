---
article_id: ind.sf_contracts_create_contract_type_and_map_to_a_contract_record_type.htm
title: Create Contract Type and Map to a Contract Record Type
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_type_and_map_to_a_contract_record_type.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm
fetched_at: 2026-10-13
---

# Create Contract Type and Map to a Contract Record Type

Using contract type, you can manage different types of contracts within an org. From Setup, you can create a contract type or clone an existing contract type and modify it and map the contract type to one or more record types.

The default contract type is mapped to the contract lifecycle management record type.

NOTE One contract type can be mapped to multiple record types. However, one record type can only be mapped to a single contract type.
Create a contract type:
From Setup, in the Quick Find box, enter Contract Type.
Click Contract Type.
Click New.
Enter these details:

Name: Enter a name for the contract type.

Sub Type: Enter record name that you want to associate with this contract type.

NOTE Sub Type is a comma-separated field that allows you to add multiple contract record types for a contract type.

Is Default: If you want to define the new contract type as the default contract type.

Save your changes.
Clone an existing contract type to create a contract type:
Click the settings icon and select Clone.
Enter these details:

List Name: Name of the contract type.

List API Name: API name of the contract type.

Select who can see the list view.

Save your changes.
