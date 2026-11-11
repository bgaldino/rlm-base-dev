---
article_id: ind.sf_contracts_object_state_transition_action.htm
title: Object State Transition Action in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_object_state_transition_action.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Object State Transition Action in Salesforce Contracts

Object State Transition Action in Salesforce Contracts

Object State Transition Action represents a junction between Object State Transition and Object State Action Definition. State transition determines the valid transition of an object from one state to another and the state action determines which action triggers which state transition.

You can create multiple object state transition actions for an object state action definition and vice versa.

Create an Object State Transition Action

To link the Object State Action Definition and Object State Transition, create an object state transition action.

From the App Launcher, find and select Object State Transition Action.
Click New.
Enter these details:

Name: The display name of the object state action transition.

Display Sequence: Determines the display order of the object state action buttons for the associated state transition. Enter a whole number greater than 0.

Object State Definition: The object state definition to associate with the contract record.

Object State Transition: The object state transition to associate with the contract record. Ensure that the selected state transition belongs to the same object state definition.

Object State Action Definition: The object state action definition to associate with the contract record.

Active: Select to activate the object state transition action.

Save your changes.
