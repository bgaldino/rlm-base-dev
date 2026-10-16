---
article_id: ind.sf_contracts_why_cant_i_create_a_contract_using_microsoft_365.htm
title: Why Can’t I Create or Edit a Contract using Microsoft 365 Word?
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_why_cant_i_create_a_contract_using_microsoft_365.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_microsoft_365_integration_troubleshooting_guide.htm
fetched_at: 2026-10-13
---

# Why Can’t I Create or Edit a Contract using Microsoft 365 Word?

To create or edit a contract using Microsoft 365, you must enable the View Setup and Configuration setting for your user profile.

NOTE This applies to customers on Summer '26 or earlier. From Winter '26 onward, non-admin and custom profile users no longer need the View Setup and Configuration admin permission to create or edit contracts in Microsoft 365 Word.

Errors

Contract document version can't be edited.

OR

We couldn't fetch the contract document version because of a configuration error or API failure. The document can't be opened in the Microsoft 365 editor. Ask your Salesforce admin for help.

Solution

From Setup, in the Quick Find box, enter Profiles and select it.
Click edit next to the profile that's assigned to the user trying to create or edit a contract using Microsoft 365.
From the Administrative Permissions section, select View Setup and Configuration.
Save your changes.
