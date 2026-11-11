---
article_id: ind.sf_contracts_default_contract_states_and_predefined_contract_actions_relationship.htm
title: Default Transitions and Actions in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_default_contract_states_and_predefined_contract_actions_relationship.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Default Transitions and Actions in Salesforce Contracts

Default Transitions and Actions in Salesforce Contracts

This reference shows the complete relationship between contract states, the actions available in each state, and the resulting state after each action runs.

How Actions Appear on a Contract

Salesforce Contracts shows an action button on a contract record only when both conditions are true:

A valid transition exists from the contract's current state to the action's target state.

The user has the required permission sets (at minimum, ContractMgmtRuntime and DocGenRuntimeUser).

NOTE System actions (Send for Signature, Revoke Signature, and Update Envelope Status) work only with the predefined contract states. These actions fail if you configure them to transition to custom state values.
States, Actions, and Transitions

This table shows every default transition: the starting state, the action that triggers the transition, the resulting state, and any associated workflow.

FROM STATE	ACTION	TO STATE	WORKFLOW
Draft	Submit for Approval	In Approval Process	Triggers approval workflow
Draft	Cancel Contract	Canceled	—
In Approval Process	Approved (by approver)	Negotiating	Approval workflow completes
In Approval Process	Rejected (by approver)	Rejected	Approval workflow completes
In Approval Process	Cancel Approval	Draft	Cancels approval workflow
In Approval Process	Cancel Contract	Canceled	Cancels approval workflow
Rejected	Re-draft Contract	Draft	—
Rejected	Cancel Contract	Canceled	—
Negotiating	Send for Signature	Awaiting Signature	Creates DocuSign envelope
Negotiating	Re-draft Contract	Draft	—
Negotiating	Cancel Contract	Canceled	—
Awaiting Signature	Update Envelope Status (signed)	Signed	Queries DocuSign status
Awaiting Signature	Update Envelope Status (declined)	Signature Declined	Queries DocuSign status
Awaiting Signature	Revoke Signature	Negotiating	Revokes DocuSign envelope
Awaiting Signature	Cancel Contract	Canceled	—
Signature Declined	Re-draft Contract	Draft	—
Signature Declined	Cancel Contract	Canceled	—
Signed	Activate Contract	Activated	—
Activated	Terminate Contract	Contract Terminated	—
Activated	(System) Expiration	Contract Expired	—
Default Object State Transition Records

These are the Object State Transition records created by the ContractManagement license. Each record defines one allowed path from one state to another.

The default Contract Lifecycle Management Object State Definition includes 19 transition records:

TRANSITION RECORD NAME	FROM STATE	TO STATE
Draft_To_InApproval	Draft	In Approval Process
Draft_To_Cancelled	Draft	Canceled
InApproval_To_Rejected	In Approval Process	Rejected
InApproval_To_Negotiating	In Approval Process	Negotiating
InApproval_To_Canceled	In Approval Process	Canceled
InApproval_To_Draft	In Approval Process	Draft
Rejected_To_Canceled	Rejected	Canceled
Rejected_To_Draft	Rejected	Draft
Negotiating_To_Draft	Negotiating	Draft
Negotiating_To_AwaitingSignature	Negotiating	Awaiting Signature
Negotiating_To_Canceled	Negotiating	Canceled
AwaitingSignature_To_Signed	Awaiting Signature	Signed
AwaitingSignature_To_SignatureDeclined	Awaiting Signature	Signature Declined
AwaitingSignature_To_Negotiating	Awaiting Signature	Negotiating
AwaitingSignature_To_Canceled	Awaiting Signature	Canceled
SignatureDeclined_To_Canceled	Signature Declined	Canceled
SignatureDeclined_To_Draft	Signature Declined	Draft
Signed_To_Activated	Signed	Activated
Activated_To_Expired	Activated	Contract Expired
Activated_To_Terminated	Activated	Contract Terminated
Predefined Dynamic Action Definitions

These are the Object State Action Definition records created by the ContractManagement license. Each record defines one action that can trigger a state transition.

ACTION	DESCRIPTION
Submit for Approval	Submits the contract for internal approval and triggers the configured approval workflow.
Cancel Contract	Cancels the contract. If the contract is in the approval process, then the approval request is canceled first.
Re-draft Contract	Returns the contract to Draft status for further editing.
Send for Signature	Sends the latest contract document version to DocuSign for the customer's e-signature.
Revoke Signature	Revokes the DocuSign envelope and returns the contract to Negotiating status.
Update Envelope Status	Queries DocuSign for the latest signature status. Moves the contract to Signed or Signature Declined based on the response.
Activate Contract	Activates the contract after signing is complete.
Terminate Contract	Terminates the entire contract or specific contract lines.
