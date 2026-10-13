---
article_id: ind.sf_contracts_workflow_to_remove_contract_status_values_from_a_contract_object_state_definition.htm
title: Workflow to Remove Contract Status Values From A Contract Object State Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_to_remove_contract_status_values_from_a_contract_object_state_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_sample_workflows_to_create_and_customize_contract_object_state_definitions.htm
fetched_at: 2026-10-13
---

# Workflow to Remove Contract Status Values From A Contract Object State Definition

You can edit the picklist values of a record type to include only certain states for a contract. For example, you can remove record type values that are specific to e-signature.

WARNING When you remove certain states from the status picklist, the corresponding actions are still be visible on the UI and work as per the default lifecycle states. Therefore, the actions may break as it will not find the corresponding states.
Create a record type without e-signature values.
From Setup, click Object Manager. Type Contract in the Quick Find box.
Click Contract and then click Record Types.
Contract Lifecycle Management is the default contract record type.
Click New.
Enter these details:

Existing Record Type: Master

Name: Name of the contract record type.

Active: Select checkbox.

Make Available: Select the user profiles that you want to provide the ability to create and clone records of this record type, or assign this record type to an existing record. To make the new record type the default for a profile, select Make Default. Users assigned to this record type can still view and edit records associated with record types not available for their profiles.

Click Next.
Select Contract Layout to Apply one layout to all profiles.
Save your changes.
Click the record type you created. Click Edit next to Status.
Using the left arrow, remove values from Selected Values to Available Values.
For example, remove all e-signature values, i.e. Awaiting Signature, Signed, Signature Declined from Selected Values to Available Values.
Save your changes.
Map default contract type with a new record type.
From Setup, in the Quick Find box, enter Contract Type.
Click Contract Type.
Click the down arrow next to the default contract type that you want to edit and then click Edit.
Enter the record type name that you created. Click Continue.
NOTE Sub Type is a comma-separated field, you can add multiple contract record types mapped to a contract type. Enable Is Default to configure this contract type as the default contract type.
Save your changes.
Test the modified contract states.
When you create a contract, the contract states won't include e-signature states as we removed them from the record type that we created in the previous steps.
Create a contract and select the record type that you created without e-signature values.
Verify the contract states, it doesn't include the e-signature states.
