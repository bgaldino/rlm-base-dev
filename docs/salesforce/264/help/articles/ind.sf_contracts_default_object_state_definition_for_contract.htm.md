---
article_id: ind.sf_contracts_default_object_state_definition_for_contract.htm
title: Default Object State Definition in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_default_object_state_definition_for_contract.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_state_models_transitions_and_actions.htm
fetched_at: 2026-10-13
---

# Default Object State Definition in Salesforce Contracts

Default Object State Definition in Salesforce Contracts

When you enable the ContractManagement license, the system creates a default Object State Definition called "Contract Lifecycle Management" with 11 states and 19 transitions.

What Gets Created

"Object State Definition" is both a Salesforce object and the name for the records stored on it. When we say "the Contract Lifecycle Management Object State Definition," we mean a specific record on the Object State Definition object.

Enabling the ContractManagement license creates:

One Object State Definition record ("Contract Lifecycle Management")

11 Object State Values (the valid contract states)

19 Object State Transitions (the allowed paths between states)

8 predefined dynamic actions bound to those transitions

NOTE The Contract Lifecycle Management Object State Definition applies only to the Contract object's Status field.
How It Maps to Contract Types

The default Object State Definition maps to the "Default" contract type. All contracts use it unless you create a custom Object State Definition and assign it to a different contract type. Define a unique lifecycle for each contract type as needed.

Object State Definition Record Fields

Each Object State Definition record is identified by four fields that bind it to a specific object, field, and contract type.

Reference Object
The object that the definition applies to. For Salesforce Contracts, this is Contract.
Reference Field
The field on the reference object that stores the state. For Salesforce Contracts, this is Status.
Additional Field
The field that distinguishes which definition to use. For Salesforce Contracts, this is ContractType.
Additional Field Value
The specific contract type that this definition applies to. For the default, this is "Default."
Active
Whether this Object State Definition is active. Only active definitions control contract behavior.
Permissions

Users with the ContractMgmtAdmin permission set can create, edit, and delete Object State Definitions.

Users with the ContractMgmtRuntime or ContractMgmtRuntimePC permission sets have read-only access.

Default Object State Values

Each Object State Value corresponds one-to-one with a contract status picklist value. If you rename a picklist value, the mapping breaks and the state model stops working.

The default Contract Lifecycle Management Object State Definition includes these 11 values:

OBJECT STATE VALUE	CONTRACT STATUS PICKLIST VALUE
Draft	Draft
In Approval Process	In Approval Process
Rejected	Rejected
Negotiating	Negotiating
Awaiting Signature	Awaiting Signature
Signature Declined	Signature Declined
Signed	Signed
Activated	Activated
Canceled	Canceled
Contract Expired	Contract Expired
Contract Terminated	Contract Terminated
IMPORTANT Maintain the one-to-one mapping between the status picklist and the Object State Value. If you rename a picklist value (for example, changing "Draft" to "New"), the mapping goes out of sync and the Object State Definition stops functioning.
