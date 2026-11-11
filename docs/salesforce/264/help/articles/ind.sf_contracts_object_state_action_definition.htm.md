---
article_id: ind.sf_contracts_object_state_action_definition.htm
title: Object State Action Definition in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_object_state_action_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Object State Action Definition in Salesforce Contracts

Object State Action Definition in Salesforce Contracts

Object State Action Definition contains details of an action, including the type of action Apex or Omniscript and the defined behavior of an action when called. For example, on an activated contract, there is a custom action called Endcontract that is configured to move the contract to terminated.

You can create multiple object state action definitions for an object state transition action and vice versa.

TIP Avoid modifying standard object state action definitions provided with your Salesforce Contracts license, as changes can cause unexpected behavior. To customize behavior or add an invocable Apex class and method, clone the standard object state action definition and use the cloned version instead. To determine whether an object state action definition is standard or custom, check the Is System field on the record. A check mark indicates a standard definition, and a blank value indicates a custom definition.

The contract state value changes when you execute the object state action definition. Here are a few variations on how an Apex class or Omniscript handles the state values.

APEX	OMNISCRIPT
Salesforce Contracts uses Apex class to trigger state transitions. Apex classes run at a system level, not at a user level.	Omniscript is customizable; configuration required for state transitions in Omniscript.


You can execute Apex actions from the contract actions API or from Salesforce Contracts. Implement Apex class callouts asynchronously.

Salesforce doesn't recommend running the Apex class directly.

	You can call Omniscript custom action only from Salesforce Contracts UI.
WARNING Any callout requests, such as HTTP, that you make while working on settings or an implementation that’s outside of Salesforce could be irreversible. Implement the rollBackAction hook in your Apex class to revert changes made outside of Salesforce. Salesforce Contracts application triggers the rollBackAction hook in case of a failure during action execution, but doesn’t guarantee success because the changes were made outside of Salesforce.
Create an Object State Action Definition using an Apex Class

To create custom action buttons, create object state action definitions that are associated with Apex classes. Configure the associated Apex class in the Developer Console before creating an object state action definition.

USER PERMISSIONS NEEDED	 
To define, edit, delete, set security, and set version settings for Apex classes:	Author Apex
To run Apex tests:	View Setup and Configuration
From the App Launcher, find and select Object State Action Definition.
Click New.
Enter these details:

API Name: A unique API name. For example, DraftToSigned.

Name: The button display name.

Invocable Class Name: The name of the Apex invocable class you created.

Invocable Method Name: The name of the Apex invocable class method. For example, executeAction.

Action Type: Apex

The action type for the object state action definition: Apex or Reference Object.

Reference Object: The Reference Object associated with the Object State Action Definition.

Save your changes.

See Also

Create an Apex Class for Object State Action Definition

Create an Object State Action Definition using Omniscript

To create custom actions, create Object state action definitions that reference Omniscripts. Create the associated Omniscript before creating an object state action definition.

IMPORTANT

Omniscripts associated with an object state action definition won’t automatically initiate state transitions. Define state transitions in the Omniscript.

You can only make API calls from the Salesforce Contracts UI.

You can’t call API for action type: Omniscript.

You must have the Omnistudio permission set license.

From the App Launcher, find and select Object State Action Definition.
Click New.
Enter these details:

API Name: A unique API name. For example, DraftToSigned.

Name: The display name of the object state action definition.

Action Type: Reference Object

Reference Object: Select the Omniscript to associate with the object state action definition.

Save your changes.

See Also

Omniscripts
