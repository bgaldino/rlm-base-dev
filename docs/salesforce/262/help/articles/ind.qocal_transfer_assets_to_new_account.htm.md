---
article_id: ind.qocal_transfer_assets_to_new_account.htm
title: Transfer Assets Between Accounts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_transfer_assets_to_new_account.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Transfer Assets Between Accounts

To maintain compliance and streamline operations, your users can move asset quantities, product licenses, or subscriptions between different accounts or contracts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create transfer quotes and orders:	Amend Assets user permission

For example, if Account A transfers 200 of its 500 Sales Cloud licenses to Account B, this process reduces Account A’s count by 200 and creates an asset for 200 licenses on Account B. This capability ensures SOX compliance by linking a quantity reduction in one account to an increase in another, eliminating manual "rip and replace" processes.

Prerequisites

Before transferring assets, configure the environment to support the enhanced quote-to-order flow.

In Setup, find and select Revenue Settings and turn on Advanced Order Creation From Quote.
In Setup, find and select Flows and select the Create Orders From Quote flow template.
Select Save as a New Flow, enter a flow label and unique API name, and activate the flow.
You can customize flow screens to configure the Order Creation method or Split field.
In Revenue Settings, add the API name of the new flow to the Set Up Flow for Creating Orders from Quotes setting.
Save your changes.
Transfer an Asset

When you initiate a transfer, the system generates two quotes: a source quote (action: Amend, subtype: TransferFrom) and a destination quote (action: Add, subtype: TransferTo). The quote header action updates to Transfer. While quantities default to the full asset amount, users can adjust them for partial transfers.

From the App Launcher, find and select the Accounts page, then select an asset in the Managed Asset Viewer on the Assets tab.
From the Amend, Renew, Cancel dropdown list, select Transfer.
On the New Transfer Details page, enter the transfer details and click Submit.
On either the source or destination quote, select Create Order to generate both a source and a destination order.
A success message confirms the creation of both orders.
Verify that the new orders appear in Draft status on the Related tab of the Account page.
Activate the source order first, and then activate the destination order. Follow this sequence to prevent transferring more quantity than exists on the source asset.
NOTE If a quantity or date mismatch occurs during destination order activation, perform manual error correction.
Assetize the source and destination orders in any sequence.
To ensure data consistency, the system blocks other amend, renew, or cancel functions on these assets until you fully assetize both orders.
