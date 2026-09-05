---
article_id: ind.qocal_asset_lifecycle_considerations.htm
title: Asset Lifecycle Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_asset_lifecycle_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_asset_lifecycle.htm
fetched_at: 2026-09-04
---

# Asset Lifecycle Considerations

This topic details known limitations for the Asset Lifecycle features of Transaction Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
Important Considerations
When you renew a bundle that includes one-time products, the system doesn't create Asset Contract Relationship records for those products. Renewal of one-time products isn't supported. The system sets the action to No Change and the quantity to zero, which prevents assetization. To manage Asset Contract Relationships for one-time products after renewal, manually create the ACR directly from the asset record on the account. See Create Asset Contract Relationships.
When amending or renewing an asset, you cannot change its price book or currency. The amendment or renewal transaction must use the same price book and currency as the initial sale.
Usage Selling Assets Considerations
Understand the limitations and behaviors of usage-based assets before setting up or selling usage products. Reviewing these requirements ensures accurate grant management, consumption tracking, and account binding throughout the asset lifecycle.
Field and Price Amendment Considerations
Familiarize yourself with the specific requirements for using Field Amendments and Price Amendments to update asset details and adjust pricing effectively. Understanding these technical mappings and supported fields helps you accurately reflect amendments in asset state periods (ASPs) and audit trails.
Transaction Rollbacks Considerations
Understand the requirements and limitations of the rollback feature to reverse the most recent transaction on an asset. Familiarizing yourself with these rules ensures data integrity and helps you determine when a transaction is eligible for reversal.
Changing Subscription End Dates of Termed Assets Considerations
Understand the requirements and limitations for modifying subscription end dates during amendments and renewals. Familiarizing yourself with these rules helps you accurately lengthen or shorten a subscription's term to meet evolving customer needs.
Zero-Quantity Quote Detail Lines Considerations
Zero-quantity quote detail lines appear when the lifecycle transaction state must be preserved even though the effective quantity for a period equals zero.
Asset Transfer Considerations
Familiarize yourself with the requirements and limitations for moving assets between accounts to ensure data consistency and compliance. Reviewing these constraints helps you manage quantities, price books, and product types correctly during the transfer process.
Swap, Upgrade, and Downgrade Amendments Considerations
Familiarize yourself with the requirements and restrictions for processing swaps, upgrades, and downgrades as specialized types of amendments. Understanding these constraints ensures accurate lifecycle management and prevents transaction errors during asset modification.
Considerations for Assets with Future-Dated Changes
Keep these considerations in mind when amending, renewing, canceling, transferring, or swapping assets with future-dated changes.
Considerations for Assets with Backdated Changes
These considerations apply when you amend, renew, or cancel an asset with an effective date in the past.
Add Assets Considerations for Amendment and Renewal Quotes and Orders
Before you add assets to an amendment or renewal quote or order, understand how the Contract lookup field affects which assets are eligible to appear in the Add Assets modal.
