---
article_id: ind.collections_customize_omniscript_for_direct_debit.htm
title: Customize the Prebuilt Omniscript for Direct Debit Request
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_omniscript_for_direct_debit.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_configure_direct_debit_setup.htm
fetched_at: 2026-08-04
---

# Customize the Prebuilt Omniscript for Direct Debit Request

Create a new version of the prebuilt Omniscript, CollectionsRequestDirectDebitForCollectionPlans, set the submit status values for the collection plan status and actionable list member status.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To customize the prebuilt Omniscript:	OmniStudio Admin
From the App Launcher, find and select OmniScripts.
Click the prebuilt OmniScript CollectionsRequestDirectDebitForCollectionPlans.
Click New Version.
Select the Set Values action, SetDebitRequestDetails.
Go to the Set Values Properties section, and click SubmitStatus.
Enter a status value, and save the changes. For example, enter Submitted.
When a collections specialist submits a direct debit request, the collection plan status value will be updated with the value that you set here.
In the Set Values Properties section, and click ActionableListMemberStatus.
Enter a status value, and save the changes. For example, enter Submitted.
When a collections specialist submits a direct debit request, the actionable list member status value will be updated with the value that you set here.
Click Activate.
