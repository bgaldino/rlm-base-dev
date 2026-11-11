---
article_id: ind.sf_contracts_object_state_transition_action_scenarios.htm
title: Object State Transition Action Scenarios in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_object_state_transition_action_scenarios.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Object State Transition Action Scenarios in Salesforce Contracts

These scenarios contain important information to keep in mind when configuring actions for a contract.

Scenario 1

The contract status doesn’t change because Apex class logic and state transition mapping doesn’t match. Here’s an example:

Contract is in Draft state.

You configure:

An object state action definition using Apex Type DraftToInApproval.

An object state transition action from Draft to In Approval for the DraftToInApproval action.

An Apex class called ChangeStatus.apxc, with logic that moves the contract from Draft to Canceled.

When you click DraftToInApproval, the contract doesn’t move from Draft to In Approval. The Apex class executes the defined logic and moves the contract from Draft to Canceled as an intermediate state.

If the object state transition includes a transition that moves the contract from Canceled to In Approval, then the contract returns to the initial Draft state.

NOTE To transition the contract from Draft to In Approval state, you must create an object state transition from Canceled to In Approval.

The final state of the contract is Draft.

Scenario 2

The contract status changes even though Apex class logic and state transition mapping don’t match—because the object state transition includes all required transitions. Here’s an example:

Contract is in Draft state.

You configure:

An object state action definition using Apex Type DraftToCanceled.

An object state transition action from Draft to Canceled for the DraftToCanceled action.

An Apex class called StatusChange.apxc, with logic that moves the contract from Draft to In Approval.

When you click DraftToCanceled, the contract moves from Draft to In Approval to Canceled because there is a default transition from InApproval_To_Canceled.

Final state of the contract is Canceled.

Scenario 3

The contract status doesn’t change when you click the object state action button because the Apex class execution already updated the contract status. Here’s an example:

Contract is in Draft state.

You configure:

An object state action definition using Apex Type DraftToInApproval.

An object state transition action from Draft to In Approval for the DraftToInApproval action.

An Apex class called ChangeStatus.apxc, with logic that moves the contract from Draft to In Approval.

When you click DraftToInApproval, since the contract is already In Approval Process because the Apex class has already executed the logic defined in the class which moves the contract from Draft to In Approval as an intermediate state. Therefore, the contract status remains In Approval as it’s a valid state.

Final state of the contract is In Approval.

Scenario 4

An object state definition has multiple associated object state transition actions. The object state transition actions have the same From state and different To states. The Salesforce Contracts application updates the status of contracts based on the defined transitions and actions. If there are differences between Apex class logic and defined transitions, the application attempts to follow the defined transitions. Here’s an example:

Contract is in Draft state.

You configure:

An object state action definition using Apex Type DraftToFinalStatus.

An object state transition action from Draft to In Approval for the DraftToFinalStatus action.

An object state transition action from Draft to Activated for the DraftToFinalStatus action.

Here are two options for configuring an Apex class and their resulting outcomes.

NOTE For the Apex calls in this scenario to succeed, the finalStatusValue parameter is mandatory.
OPTION	SCENARIOS
Create an Apex class called ChangeStatus.apxc, with logic that moves the contract from Draft to In Approval.	

If the finalStatusValue is set to In Approval Process, the contract moves from Draft to In Approval Process.

If finalStatusValue is set to Activated, the transition fails because the path isn’t defined from In Approval Process to Activated. The contract remains in Draft state.


Create an Apex class called ChangeStatus.apxc, with logic that moves the contract from Draft to Activated.	

If the finalStatusValue is set to Activated, the contract moves from Draft to Activated.

If finalStatusValue is set to In Approval Process, the transition fails because the path isn’t defined from Activated to In Approval Process. The contract remains in Draft state.
