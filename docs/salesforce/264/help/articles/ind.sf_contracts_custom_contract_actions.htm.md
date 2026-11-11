---
article_id: ind.sf_contracts_custom_contract_actions.htm
title: Use Custom Actions To Change Contract Status
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_custom_contract_actions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_spring_23_release_notes.htm
fetched_at: 2026-10-13
---

# Use Custom Actions To Change Contract Status

Contract actions perform a predefined action and change the contract’s status between two valid states. Now, you can configure and use custom contract actions along with the predefined dynamic (contract) actions. You can create custom actions by using an Apex Class or Omniscript.

You can use custom actions for:

State transitions: Determine the permissible state transition of an object from one state to another by using specific actions.

Application behavior modification: Configure Apex Class or Omniscript to change how an application works within Salesforce. Salesforce admins must be careful as some modifications are irreversible.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, Professional, and Developer editions.

Who: Available for users with the minimum ContractMgmtRuntime permission sets.
