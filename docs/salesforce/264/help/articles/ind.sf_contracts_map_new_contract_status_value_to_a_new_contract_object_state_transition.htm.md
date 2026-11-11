---
article_id: ind.sf_contracts_map_new_contract_status_value_to_a_new_contract_object_state_transition.htm
title: Map New Contract Status Value to a New Contract Object State Transition
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_map_new_contract_status_value_to_a_new_contract_object_state_transition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_configure_new_contract_status_values_and_map_to_contract_object_state_definition.htm
fetched_at: 2026-10-13
---

# Map New Contract Status Value to a New Contract Object State Transition

You must associate the new contract status value to the new contract object state transition using the contract object state definition so that the new status values reflect in the contract states bar.

Using the App Launcher, open Object State Definition.
Select the contract state definition that you want to update.
For example, select the default Contract Lifecycle Management.
From the Related tab, scroll to the Object State Transitions section, and click New.
Enter these details:
Name: Name for the new state transition. For example, Draft_To_In Approval Process.
From State: Select a From State value for the contract.
To State: Select a To transition state value for the contract.
Save your changes.
From the Details tab, select the Active checkbox and save your changes.
Test New Contract Status:
Open a contract.
From the Details tab, ensure that the Is Associated with CLM checkbox is selected.
For more information, see Is Associated with CLM.
From the contract states bar, select the new transition state and click Mark Status as Complete. If the mapping is correct, the status change is successful.
