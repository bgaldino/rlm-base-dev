---
article_id: ind.sf_contracts_update_sharing_settings_for_omni_objects.htm
title: Update Sharing Settings for Omni Objects in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_update_sharing_settings_for_omni_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-10-13
---

# Update Sharing Settings for Omni Objects in Salesforce Contracts

To make the Omni object records created by a user accessible to all the users within an org, you need to update the sharing settings.

From Setup, in the Quick Find box, enter sharing.
Click Sharing Settings.
Click Edit.
Provide access to these Omni objects:
OBJECT	DEFAULT INTERNAL ACCESS	DEFAULT EXTERNAL ACCESS (IF NEEDED)
Omni DataPack	Public Read Only	Private
Omni Data Transformation	Public Read Only	Private
Omni Process	Public Read Only	Private
Omni Process Transient Data	Public Read Only	Private
Save your changes.
To allow external users to access the specific records, define the sharing criteria.
Access the object that you want to modify.
To create criteria-based sharing rules. See Create Criteria-Based Sharing Rules.
For the rule type, select Based on criteria, and set these values.
SETTING	VALUE
Field	Created By ID
Operator	Start With
Value	005

The 005 prefix identifies user IDs. This criterion grants access to records created by users with this ID.

Save your changes.
