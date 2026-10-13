---
article_id: ind.sf_contracts_workflow_to_create_a_custom_object_state_action_definition.htm
title: Workflow to Create a Custom Object State Action Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_to_create_a_custom_object_state_action_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_sample_workflows_to_create_and_customize_contract_object_state_definitions.htm
fetched_at: 2026-10-13
---

# Workflow to Create a Custom Object State Action Definition

You can create an Object State Definition (state model) with specific Object State Values and Object State Transitions. In the Object State Definition, you can define custom actions that call specific transitions using an Apex Class or Omniscript.

In this example, we’re creating a simple state model that moves a contract from draft to signed using the Sign Contract custom action button.

NOTE Object State Models are only supported for use in Salesforce Contracts. Only the CLM Admin User can configure object state models; other Salesforce Contract users can view and generate documents using the object state models.
Create a contract record type.
Contract Record Type groups multiple contract records for a specific contract type under a contract object. Contract record types allow you to have a different page layout, and fields (required or not) with different picklist values. See Create Contract Record Type.
Create a contract type and map it to a contract record type.
Use Contract Type to manage different types of contracts within an org. From Setup, create a contract type or clone and modify an existing contract type. Then, map the contract type to one or more contract record types. See Create Contract Type and Map to a Contract Record Type.
Create an object state definition.
From the App Launcher, find and select Object State Definition.
Click New.
Enter these details:

Name: Name for your object state definition.

Reference Object: Contract

Reference Field: Status

Additional Field: ContractType

Additional Field Value: Name of the contract type to map to this object Object State Definition.

NOTE The Object State Definition you created has no default state values or transitions. You need to configure these values.
Create object state values.
From the App Launcher, find and select Object State Definition.
Click the object state definition that you created in the previous step.
Click the Related tab.
From the Object State Values section, click New.
Enter these details:

Name: Name for your state value. For example, Draft.

Description: Description for the state value.

Reference Record Access Type: ReadOnly

Object State Definition: The field is populated by default.

Save your changes.
Repeat the above steps to add more state values. For example, Signed.
Configure contract status picklist values.
The Contract Status field controls the contract Object State Definition. Salesforce Contracts provides a default set of contract status picklists, it includes draft and signed. You can create additional contract status picklists and reorder the sequence of contract status values from Setup.
ATTENTION The one-to-one mapping between the status picklist and the object state value and its order must be maintained. For example, if you change the Draft status picklist value to New, the mapping between that status and its corresponding object state value becomes out of sync and the Object State Definition won’t work. For more information, see Default Contract Status Picklist Values.
From Setup, click Object Manager.
Click Contract,and then click Fields & Relationships.
Click Status.
In the Contract Status Picklist Values section, click New.
Enter a Label and API name.
Select a default status category from the list.
Select the record type for the status.
Save the changes.
To reorder the picklist value, click Reorder.
Use the arrow keys to reorder the picklist values.
Save your changes.
Create object state transitions.
From the App Launcher, find and select Object State Definition.
Click the object state definition you created.
Click the Related tab.
In the Object State Transitions section, click New.
Enter these details:

Name: Name for your state transitions value. For example, Draft_To_Signed.

From State: Enter the state to transition from. For example, Draft.

To State: Enter the state to transition to. For example, Signed.

Description: Description for the state value.

Object State Definition: The field is populated by default.

Save your changes.
Repeat the above steps to add more state transitions.
Select Active on the Object State Definition and save your changes.
Create an object state action definition.
By creating an object state action definition, you're defining a custom action button based on an Apex class or Omniscript. Use one of these options:

Create an Object State Action Definition using Apex Class

Create an Object State Action Definition using Omniscript

Create an object state transition action.
To link the object state action definition and object state transition, create an object state transition action. For more information, see Create an Object State Transition Action
Configure contract type configs.
At a minimum, configure the DocumentFileNameFormat, and AutoGenerateDocFileType contract type configuration values. For more information, see Create Contract Type Config Setting. To view all the available settings, see Contract Type Config Settings.
Test your custom action on a contract.
Create a contract.
From the Documents tab, click the custom action you created.

For Omniscripts, the Omniscripts modal opens based on your configuration.

For Apex classes, the status of the contract moves based on the defined custom action.
