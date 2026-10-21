---
article_id: ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm
title: Contract Types, Contract Record Types, and Contract Type Configs
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Contract Types, Contract Record Types, and Contract Type Configs

Contract record types, contract types, and contract type configs work together to control how contracts behave throughout their lifecycle.

These three objects form a hierarchy. A contract record type maps to a contract type, which has contract type config settings. When you create a contract, the application assigns a contract type based on the record type you select. The contract type determines the contract's state model, lifecycle, and configuration settings.

Contract Record Type
Groups contract records under a contract object. Each record type can have its own page layout, required fields, and picklist values. A record type is mapped to a user profile.

A contract record type can have only one parent contract type, but a contract type can have multiple child record types. If a record type has no parent contract type, the application automatically associates its contracts with the default contract type.

Contract Type
Classifies contracts into categories such as sales contracts, non-disclosure agreements, or partnership agreements. For each contract type, you can define contract stages, approval processes, object state definitions (state models), and associated document templates.

Use contract types to configure different lines of business separately. For example, if your company has three business lines that use Contract Lifecycle Management, create a separate contract type for each and configure the appropriate options independently.

Contract Type Config
A set of configuration settings that control contract behavior for a specific contract type. Settings include document attachment formats, default template associations, review options, and notification preferences. For a full list, see Contract Type Config Settings.
Default Configuration

When you enable the ContractManagement license, the application creates a default contract type, record type, and contract type config.

CONTRACT TYPE	CONTRACT RECORD TYPE	CONTRACT TYPE CONFIG
Default	Contract Lifecycle Management	Contract Type Config Settings
NOTE By default, the Contract Type field on a contract is read-only. To allow runtime users to modify this field, enable the setting at the profile level.
Mapping Contract Record Type to Contract Type
You can create a new contract record type, and a contract type and then map the contract type to the new record type.
Create Contract Record Type
A contract record type can have only one contract type object as its parent, but a contract type object can have multiple contract record types as its child.
Create Contract Type and Map to a Contract Record Type
Using contract type, you can manage different types of contracts within an org. From Setup, you can create a contract type or clone an existing contract type and modify it and map the contract type to one or more record types.
Edit or Delete a Contract Type
You can modify a contract type by associating additional record types or you can replace the existing record type with another record type. You can also delete a contract type from Setup.
