---
article_id: ind.qocal_assetize_assets.htm
title: Update Assets to Reflect Changes by Using Flows
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_assetize_assets.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_manage_assets_in_revenue_lifecycle_management.htm
fetched_at: 2026-09-04
---

# Update Assets to Reflect Changes by Using Flows

Update your assets after completing amendment, renewal, or cancellation changes to your quotes or orders. This process ensures that your assets accurately reflect modifications made to the asset lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To amend, renew or cancel assets:	

InitiateAmendment API, InitiateRenewal API, and InitiateCancellation API permission sets

AND

Sales Rep persona permissions


To open, edit, or create a flow in Flow Builder:	Manage Flow
To activate object state definitions:	Assetize Order permission set

Trigger the same flow you created and activated in Automate the Creation and Update of Assets from Orders by Using Flows to update your assets. Running this flow synchronizes your asset records with the final changes from your amendment, renewal, or cancellation transactions.
