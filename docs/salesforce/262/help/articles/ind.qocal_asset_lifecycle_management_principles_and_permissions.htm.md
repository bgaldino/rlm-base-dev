---
article_id: ind.qocal_asset_lifecycle_management_principles_and_permissions.htm
title: Asset Lifecycle Management Principles and Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_lifecycle_management_principles_and_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Asset Lifecycle Management Principles and Permissions

Learn more about key terms and the permissions necessary to use Asset Lifecycle Management.

Asset Lifecycle Management Principles

To use asset management, understand the crucial designs, data structures, and interactions that govern the system. Understand these terms that help users successfully use Asset Management features.

Assetization
After completing quote or order changes for an amendment, renewal, or cancellation, update your assets by using a flow to reflect the lifecycle changes.
Asset State Periods (ASPs)
ASPs represent the state of an asset over a period. Changes to assets create accurate asset state periods to provide parity for complex global subscription management.
Data Integrity and Audits
The transaction system maintains a complete and accurate history of all transactions through a ledger-style approach. Asset-level audit trails track all rate and grant modifications.
Last In First Out (LIFO)
If an asset consists of multiple prior sales transactions, use the LIFO strategy to compute the quote line item’s total price for negative quantities.
Managed Asset Viewer
A component added to the Account or Contract page layout that helps users to view and manage the asset lifecycle.
Future-Dated Changes
After completing quote or order changes for an amendment, renewal, or cancellation, update your assets by using a flow to reflect the lifecycle changes.
Rollback
A feature used to reverse the most recent future-dated amendment or renewal to restore an asset to its original state.
Proration
The transaction system automatically recalculates and prorates grants for usage-based products based on the asset's actual lifecycle during amendments or cancellations.
Asset Lifecycle Permissions

Before you begin managing assets, make sure that you have the necessary user permissions to perform successful feature adoption.

Assign user permissions based on the specific lifecycle task that you perform.

TASK	USER PERMISSIONS NEEDED
View Assets	Read, Create, Edit, and Delete access on Assets to manage assets and use the Managed Asset Viewer component.
Amend Assets	

InitiateAmendment API permission set

AND

Sales Rep persona permissions


Renew Assets	

InitiateRenewal API permission set

AND

Sales Rep persona permissions


Cancel Assets	

InitiateCancellation API permission set

AND

Sales Rep persona permissions


Time Zone Precision	To specify time precision on quotes, users need Create on Quotes and the PlaceOrder API permission set for orders.
