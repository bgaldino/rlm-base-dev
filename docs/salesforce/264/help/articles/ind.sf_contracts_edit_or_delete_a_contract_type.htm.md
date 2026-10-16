---
article_id: ind.sf_contracts_edit_or_delete_a_contract_type.htm
title: Edit or Delete a Contract Type
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_edit_or_delete_a_contract_type.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm
fetched_at: 2026-10-13
---

# Edit or Delete a Contract Type

You can modify a contract type by associating additional record types or you can replace the existing record type with another record type. You can also delete a contract type from Setup.

One contract type can be mapped to multiple record types. However, one record type can only be mapped to a single contract type.

IMPORTANT If you delete, add or modify a record type mapping with a contact type, the changes will only apply to the new contracts because new contracts take the updated mapping as default values. To update the existing contracts with out-of-sync contract types, the system admin can run a custom code. For more information, see Sample Code To Update Out-of-Sync Contract Type Mapping.
Modify a contract type:
From Setup, in the Quick Find box, enter Contract Type.
Click Contract Type.
Click the down arrow next to the contract type that you want to edit and then click Edit.
Enter record type names that you want to add.
Sub Type is a comma-separated field that allows you to add multiple contract record types for a contract type. Enable Is Default to configure this contract type as the default contract type.
Click Continue.
Delete a contract type:
From Setup, in the Quick Find box, enter Contract Type.
Click Contract Type.
Click the down arrow next to the contract type that you want to delete and then click Delete.

You can't delete a contract type if one or more contracts are associated with the contract type.
