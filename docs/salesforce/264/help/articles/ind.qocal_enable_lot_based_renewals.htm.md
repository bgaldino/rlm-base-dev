---
article_id: ind.qocal_enable_lot_based_renewals.htm
title: Use Lot-Based Renewals to Preserve Original Prices
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_enable_lot_based_renewals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_specialized_transaction_types.htm
fetched_at: 2026-09-04
---

# Use Lot-Based Renewals to Preserve Original Prices

To honor existing prices at renewal time, use lot-based or As-Is renewals to renew asset lot quantities at their original purchase prices. For example, if a sales rep sells an asset across multiple transactions, a lot-based renewal includes both the initial sale and subsequent amendments. The system applies a price uplift individually to each lot based on the renewal uplift.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create as-is renewals:	

InitiateRenewal API permission set

AND

Sales Rep persona permissions

IMPORTANT You use lot-based renewals only when you turn on the As-Is renewals setting. See Enable Revenue Settings. Before you generate a renewal with As-Is Renewals enabled, set the asset's Pricing Source field to Last Transaction Price. If you leave Pricing Source blank or set it to another value, the renewal will be priced at the current list price instead of preserving the original purchase prices.
In the App Launcher, search for and select Assets.
To view all sales transactions for an asset, select an asset and select the Related tab.
Review Asset Actions to see prior sales transactions.

Asset Record

In App Launcher, search for and select Accounts. On the Account page under the Assets tab, select the asset that you want to renew.
To generate a new quote, in the Managed Assets viewer, select Renew.
Under the Quote Line Items tab, on the renewal quote, select View on the product's line.
To review the quote line detail records, under the Related tab, select View All.
The quote line details show the breakdown of the prices honored for lot-based pricing.
