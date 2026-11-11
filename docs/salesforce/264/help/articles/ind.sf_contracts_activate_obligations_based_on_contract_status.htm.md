---
article_id: ind.sf_contracts_activate_obligations_based_on_contract_status.htm
title: Activate Obligations Based on Contract Status
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_activate_obligations_based_on_contract_status.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_obligation_management.htm
fetched_at: 2026-10-13
---

# Activate Obligations Based on Contract Status

Configure the Activate Obligations Based on Contract Status setting to control when obligations transition from On Hold to Active, Inactive, or Expired. The default value is Activated.

For example, the Activate Obligations Based on Contract Status contract type config setting is defined as Activated. When the contract status changes to Activated, the state of the obligation changes to Active.

Also, an email notification is sent when the state of the obligation changes if you set up the Contractual Obligations notification type. See Manage Notification Delivery Settings for Obligations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 


To define obligation notification settings:

	

CLM Admin User

From Setup, in the Quick Find box, enter Contract Type Config.
Click Contract Type Config.
Click Edit on Activate Obligations Based On Contract Status setting.
Review the default values are:

Contract Type: Default

Usage Type: Obligation Setting

Config Type: Activate Obligations Based On Contract Status

Config Value: {Activated}

If required, you can update the config value. The contract's impact on the obligation state is defined using the config value. The state of obligations associated with a contract is updated based on the change in the contract's status.

Click Continue.

See Also

Relation Between Contract Status and Obligation State
