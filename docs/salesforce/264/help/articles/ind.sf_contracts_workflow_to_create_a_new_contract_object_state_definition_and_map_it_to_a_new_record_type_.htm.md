---
article_id: ind.sf_contracts_workflow_to_create_a_new_contract_object_state_definition_and_map_it_to_a_new_record_type_.htm
title: Workflow to Create a New Contract Object State Definition and Map it to a New Record Type
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_to_create_a_new_contract_object_state_definition_and_map_it_to_a_new_record_type_.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_sample_workflows_to_create_and_customize_contract_object_state_definitions.htm
fetched_at: 2026-10-13
---

# Workflow to Create a New Contract Object State Definition and Map it to a New Record Type

You can create a new Object State Definition with specific Object State Values and Object State Transitions. Then create a record type and edit the picklist values of a record type to include only certain states for a contract. When you create a contract, the contract states only includes states that you kept in the record type status.

Create an Object State Definition.
From the App Launcher, find and select Object State Definition.
Click New.
Enter these details:

Name: Name for your Object State Definition.

Reference Object: Contract.

Reference Field: Status.

Additional Field: ContractType.

Additional FIeld Value: Name of the contract type that you want to map to this object state definition.

Save your changes.
The Object State Definition that you created has no default state values or state transitions. You need to configure these values.
Create Object State Values.
From the App Launcher, find and select Object State Definition.
Click the object state definition that you created in the previous step.
Click the Related tab.
From the Object State Values section, click New.
Enter these details:

Name: Name for your state value. For example, Draft.

IMPORTANT The one-to-one mapping between the status picklist and the object state value must be maintained. For example, if you make changes to the status picklist values, i.e. modify Draft to New, then the mapping goes out of sync with the object state value and the Object State Definition won't work.

Description: Description for the state value.

Reference Record Access Type: ReadOnly.

Object State Definition: The field is populated by default.

Save your changes.
Repeat steps a to f to add additional object state values.
Create Object State Transitions.
From the App Launcher, find and select Object State Definition.
Click the object state definition you created.
Click the Related tab.
From the Object State Transitions section, click New.
Enter these details:

Name: Name for your state transitions value. For example, Draft_To_InApprovalProcess.

From State: Enter the From state. For example, Draft.

To State: Enter the To state. For example, In Approval Process.

Description: Description for the object state transition value.

Object State Definition: The field is populated by default.

Save your changes.
Repeat steps a to f to add additional object state transitions.
Select Active on the Object State Definition and save your changes.
Create a Record Type.
From Setup, click Object Manager.
Type Contract in the Quick Find box.
Click Contract and then click Record Types.
Click New.
Enter these details:

Existing Record Type: Master.

Name: Name of the contract record type.

Active: Select the Active checkbox.

Make Available: Select the user profiles that you want to provide the ability to create and clone records of this record type, or assign this record type to existing records. To make the new record type the default for a profile, select Make Default. Users assigned to this record type can still view and edit records associated with record types not available for their profiles.

Click Next.
Select Contract Layout in Apply one layout to all profiles.
Save your changes.
Click the record type you created. Click Edit next to Status.
Using the left arrow, remove all the values that you don’t want from Selected Values to Available Values.
For example, only keep Draft, In Approval Process, Canceled, and Activated.
Save your changes.
Test the new Object State Definition with custom state values and transitions.
Create a contract and select the record type that you created.
The contract only has four states that you mapped in the record type: Draft, In Approval Process, Canceled, and Activated.
