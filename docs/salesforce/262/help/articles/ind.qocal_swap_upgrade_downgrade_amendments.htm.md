---
article_id: ind.qocal_swap_upgrade_downgrade_amendments.htm
title: Swap, Upgrade, or Downgrade Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_swap_upgrade_downgrade_amendments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Swap, Upgrade, or Downgrade Assets

To maintain accurate records and streamline your sales process, use specific asset actions to capture the relationships between swapped-out and swapped-in assets.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create a swap, upgrade, or downgrade amendment:	Initiate Amend user permission

Before you begin, add the Type and Subtype columns to the Sales Transaction Line Table component. The Type column shows action types, while the Subtype column shows line groupings like SwapIn, SwapOut, UpgradeFrom, UpgradeTo, DowngradeFrom, and DowngradeTo. SeeAdd and Customize the Transaction Line Editor or Sales Transaction Line Editor.

Instead of "rip and replace," this feature tracks swaps, upgrades, and downgrades across quote lines, order items, asset actions, and asset action sources.

Explicit labels for asset actions provide clarity for reports and audits. Business analysts and sales operations generate reports to differentiate products acquired through new sales versus amendments and to understand how these actions impact revenue.

From the App Launcher, find and select Accounts, click an account, and then select the Assets tab to open the Managed Assets viewer.
Select the assets to swap out and select Swap from the actions dropdown.
Select a date for the swap from the Swap Selections page.
Select the products to swap out, enter the quantity, and click Next.
Click Add for the products that you want to swap in, and click Next.
The resulting quote shows the line item for the swapped-out product with a negative price and the swapped-in product with a positive price.
Click Create Order, and then click Create Single Order to initiate the quote-to-order process.
Select the new order, activate it, and mark it as complete.

Review the asset actions to verify the transaction details.

In the Managed Assets viewer, select View for the swapped-out asset and select the Related tab.
Confirm that a new asset action exists with a Swaps Business Category and a negative quantity.
In the Managed Assets viewer, select View for the swapped-in asset and select the Related tab.
Confirm that a new asset action exists with a Swaps Business Category and a positive quantity.
