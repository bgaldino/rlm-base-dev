---
article_id: ind.qocal_enable_lot_based_renewals.htm
title: Use Lot-Based Renewals to Preserve Original Prices
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_enable_lot_based_renewals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Use Lot-Based Renewals to Preserve Original Prices

To honor existing prices at renewal time, use lot-based or As-Is renewals to renew asset lot quantities at their original purchase prices. For example, if a sales rep sells an asset across multiple transactions, a lot-based renewal includes both the initial sale and subsequent amendments. The system applies a price uplift individually to each lot based on the renewal uplift.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create as-is renewals:	

InitiateRenewal API permission set

AND

Sales Rep persona permissions

IMPORTANT You use lot-based renewals only when you turn on the As-Is Renewals setting. See Enable Revenue Settings.
In the App Launcher, search for and select Assets.
To view all sales transactions for an asset, select an asset and select the Related tab.
Review Asset Actions to see prior sales transactions.

Asset Record

In App Launcher, search for and select Accounts. On the Account page under the Assets tab, select the asset that you want to renew.
To generate a new quote, in the Managed Assets viewer, select Renew.
Under the Quote Line Items tab, on the renewal quote, select View on the product's line.
To review the quote line detail records, under the Related tab, select View All.
The quote line details show the breakdown of the prices honored for lot-based pricing.
