---
article_id: ind.qocal_asset_lifecycle_considerations.htm
title: Asset Lifecycle Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_lifecycle_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Asset Lifecycle Considerations

This topic details known limitations for the Asset Lifecycle features of Transaction Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
IMPORTANT

When you renew a bundle that includes one-time products, the system doesn't create new Asset Contract Relationship records for those one-time products. Renewal of one-time products isn't a supported use case. During renewal, the system sets the action to No Change and the quantity to zero for one-time products, which prevents assetization from occurring.

To manage Asset Contract Relationships for one-time products after renewal, manually create the ACR directly from the asset record on the account. See Create Asset Contract Relationships.

Usage Selling Assets Considerations
Understand the limitations and behaviors of usage-based assets before setting up or selling usage products. Reviewing these requirements ensures accurate grant management, consumption tracking, and account binding throughout the asset lifecycle.
Ramped Asset Management Considerations
Familiarize yourself with specific requirements for amending, renewing, or canceling ramped assets to manage multi-segment deals effectively. These considerations ensure data consistency and help you navigate system limitations across different ramp configuration settings.
Field and Price Amendment Considerations
Familiarize yourself with specific requirements for using the field and price amendments feature to update asset details and adjust pricing effectively. Understanding these technical mappings and supported fields makes sure that your amendments accurately reflect in asset state periods (ASPs) and audit trails.
Transaction Rollbacks Considerations
Understand the requirements and limitations of the rollback feature to reverse the most recent transaction on an asset. Familiarizing yourself with these rules ensures data integrity and helps you determine when a transaction is eligible for reversal.
Changing Subscription End Dates of Termed Assets Considerations
Understand the requirements and limitations for modifying subscription end dates during amendments and renewals. Familiarizing yourself with these rules helps you accurately lengthen or shorten a subscription's term to meet evolving customer needs.
Asset Transfer Considerations
Familiarize yourself with the requirements and limitations for moving assets between accounts to ensure data consistency and compliance. Reviewing these constraints helps you manage quantities, price books, and product types correctly during the transfer process.
Swap, Upgrade, and Downgrade Amendments Considerations
Familiarize yourself with the requirements and restrictions for processing swaps, upgrades, and downgrades as specialized types of amendments. Understanding these constraints ensures accurate lifecycle management and prevents transaction errors during asset modification.
Considerations for Assets with Future-Dated Changes
Keep these considerations in mind when amending, renewing, canceling, transferring, or swapping assets with future-dated changes.
