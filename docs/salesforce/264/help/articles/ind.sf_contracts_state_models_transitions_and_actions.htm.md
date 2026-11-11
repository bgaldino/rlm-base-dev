---
article_id: ind.sf_contracts_state_models_transitions_and_actions.htm
title: State Models and Transitions in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_state_models_transitions_and_actions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# State Models and Transitions in Salesforce Contracts

State models define the stages a contract moves through during its lifecycle and the allowed transitions between those stages. Salesforce Contracts includes a default state model. Extend it with custom states and transitions to match your business process.

How State Model Objects Relate to Each Other

State models use five objects that form a hierarchy:

Object State Definition — The top-level container. It references a base object (such as Contract) and a field (such as Status), and groups together all the valid states and transitions for that object.

Object State Values — The valid states within a definition. Each value corresponds to one picklist value on the referenced field. For example: Draft, Negotiating, Activated.

Object State Transitions — The allowed paths between two states. Each transition specifies a From state and a To state. For example: Draft → In Approval Process.

Object State Action Definitions — The actions that trigger transitions. Each action definition specifies the action type (Apex class or Omniscript) and what it does.

Object State Transition Actions — Junction records that bind an action definition to a specific transition. They also control the display order of action buttons on the contract record.

How It Works

Each contract type maps to one Object State Definition. When a user clicks an action button on a contract record, the system checks whether a valid transition exists from the current state. If it does, the associated action runs and the contract moves to the new state. If no valid transition exists, the button doesn't appear.

Salesforce Contracts includes a default Object State Definition called "Contract Lifecycle Management." Use it as-is or create custom definitions for different contract types.

Contract Lifecycle Stages
Every contract moves through a series of stages from creation to activation. The default state model implements these stages as contract statuses with defined transitions between them.
Default Object State Definition in Salesforce Contracts
When you enable the ContractManagement license, the system creates a default Object State Definition called "Contract Lifecycle Management" with 11 states and 19 transitions.
Contract Status Picklist Values in Salesforce Contracts
The Contract Status picklist field drives the state model. The ContractManagement license adds default values to this field that map to the Object State Definition.
Default Transitions and Actions in Salesforce Contracts
This reference shows the complete relationship between contract states, the actions available in each state, and the resulting state after each action runs.
Prerequisites For Setting Up State Models, State Transitions, and Actions
To set up State Models, State Transitions, and Actions, as a system administrator, make sure that you have the required licenses and permissions.
Object State Action Definition in Salesforce Contracts
Object State Action Definition contains details of an action, including the type of action Apex or Omniscript and the defined behavior of an action when called. For example, on an activated contract, there is a custom action called Endcontract that is configured to move the contract to terminated.
Object State Transition Action in Salesforce Contracts
Object State Transition Action represents a junction between Object State Transition and Object State Action Definition. State transition determines the valid transition of an object from one state to another and the state action determines which action triggers which state transition.
Create an Apex Class for Object State Action Definition
Create an invocable Apex class in the Developer Console for each of the object state action definitions (custom actions).
Object State Transition Action Scenarios in Salesforce Contracts
These scenarios contain important information to keep in mind when configuring actions for a contract.
Sample Workflows to Create and Customize Contract Object State Definitions
You can customize or create contract Object State Definitions as per your business needs. This sections details few sample customizations.
