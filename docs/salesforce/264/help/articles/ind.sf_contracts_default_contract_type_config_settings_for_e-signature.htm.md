---
article_id: ind.sf_contracts_default_contract_type_config_settings_for_e-signature.htm
title: Default Contract Type Config Settings for E-Signature
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_default_contract_type_config_settings_for_e-signature.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
fetched_at: 2026-10-13
---

# Default Contract Type Config Settings for E-Signature

Default Contract Type Config Settings for E-Signature

Salesforce Contracts application provides a default set of signature settings for the contract such as defining the default reminders and expiry warnings for the envelopes submitted for e-signatures.

NOTE You must use the Electronic Signature Envelope Config to define the default reminders and expiry for the envelopes submitted for e-signatures for custom objects and standard objects such as opportunity, quote, and order.

These settings are included by default when you install Salesforce Contracts. Verify that these settings exist in your org. If any are missing, create them using the steps in Create Contract Type Config Setting. Modify the default values only if your organization’s e-signature requirements differ from the defaults.

Here’s the list of default signature settings in the contract type config for the Contract object:

CONFIG TYPE NAME	DEFAULT CONFIG VALUE	USAGE TYPE	DESCRIPTION
Contract Signature Declined Status	Signature Declined	Signature Setting	Sets the contract document to Signature Declined status if the signer declines to sign the contract.
Contract Signed Status	Signed	Signature Setting	Sets the contract document to Signed status once the signer signs the contract.
DocuSign Expire Enabled	Yes	Signature Setting	Specifies whether the contract expires after the envelope is sent for e-signatures.
DocuSign Expire Warning	1	Signature Setting	Specifies the number of days before envelope expiration that a warning is sent.
DocuSign Expires After	5	Signature Setting	Specifies the number of days after sending the contract for e-signatures that the envelope expires if it is not signed.
DocuSign Reminder Delay In Days	2	Signature Setting	Specifies the number of days after which the e-signatures reminders are sent.
DocuSign Reminder Enabled	Yes	Signature Setting	Specifies whether the reminders are sent for e-signatures.
DocuSign Reminder Frequency	1	Signature Setting	Specifies how frequently the reminders are sent.
DocuSign Use Account Default Notification	No	Signature Setting	Specifies the settings for sending an email notification for envelope signature using DocuSign.
Create Contract Type Config Setting

You can create contract type config settings for a specific contract type.

Create a contract type config setting when you need to override the default e-signature behavior for a specific contract type. For example, you might set different expiration or reminder values for a contract type that requires longer signing windows.

From Setup, in the Quick Find box, enter Contract Type Config, and then select Contract Type Config.
Click New.
Enter the details for your contract type config.
Select a contract type.
Select a usage type.
Select a config type.
Enter a config value.
Click Create.
Edit Contract Type Config Setting

You can edit the config type settings for the contract object.

From Setup, in the Quick Find box, enter Contract Type Config, and then select Contract Type Config.
Click the dropdown arrow next to the configuration that you want to edit and click Edit.
Edit the required details.
To save your changes, click Continue.
