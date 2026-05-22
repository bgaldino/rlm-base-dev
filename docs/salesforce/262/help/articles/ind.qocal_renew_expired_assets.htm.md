---
article_id: ind.qocal_renew_expired_assets.htm
title: Renew Expired Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renew_expired_assets.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Renew Expired Assets

To maintain customer relationships and close deals faster, renew assets and subscriptions after their original end date. Enabling late renewals and trial extensions provides flexibility when customers want to repurchase products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To renew expired assets:	

InitiateRenewal API permission set

AND

Sales Rep persona permissions

You can change the asset start date even if the subscription renewal date occurs after the subscription end date. The renewal term's start date falls on or after the lifecycle end date. If a gap exists between the asset expiration date and the new renewal start date, the system updates the asset with a new asset state period of zero quantity. Selecting a renewal start and end date overrides the existing subscription renewal term and creates a quote or order to refund the unused portion of the subscription.

In the App Launcher, search for and select Accounts.
From the Assets tab of an account's page, select the asset you want to review.
Select Renew.
To select a new renewal term start date, on the Set Renewal Term prompt, select Override Renewal Term and a date.
To save your changes, click Submit.
