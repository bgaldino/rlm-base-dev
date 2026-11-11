---
article_id: ind.sf_contracts_disable_vlocity_state_models_trigger.htm
title: Disable Vlocity State Models Trigger
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_disable_vlocity_state_models_trigger.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_salesforce_contracts_in_vlocity_managed_packages.htm
fetched_at: 2026-10-13
---

# Disable Vlocity State Models Trigger

To use the Salesforce Contracts features in an org, the contract admin must disable the Vlocity State Models trigger so that Salesforce Contracts can use the default Contract Lifecycle Management object state definitions. You must disable the trigger in the orgs where Omnistudiio licenses are provisioned first, followed by the installation of the Vlocity managed package (CME or INS).

IMPORTANT When you enable the ContractManagement license, the default Contract Lifecycle Management object state definition, its corresponding object state values, and object state transitions are created.
REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To disable the Vlocity State Models trigger:	CLM Admin
From Setup, in the Quick Find box, enter Custom Settings.
Click T, find Trigger Setup, and click Manage.
Click Contract.EnableStateModel, and then deselect Trigger On.
Save your changes.
