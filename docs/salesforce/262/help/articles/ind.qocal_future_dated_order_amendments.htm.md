---
article_id: ind.qocal_future_dated_order_amendments.htm
title: Future-Dated Changes
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_future_dated_order_amendments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Future-Dated Changes

To adjust assets that have scheduled future transactions, such as upsells, downsells, renewals, transfers, swaps, or attribute changes, use the Managed Asset viewer. This process updates assets that have more than one subsequent future-dated change recorded as an asset state period (ASP).

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To amend, transfer, or use swaps in orders with future-dated asset state periods:	Initiate Amend user permission or initiateAmendment API access
To renew and cancel orders:	

Initiate Renew and Initiate Cancel user permissions

OR

initiateRenew API and initiateCancel API access

sThe transaction system creates a regular amend, renew, or cancel transaction if the transaction has only one ASP or occurs in the last ASP. Changing an asset before a future ASP on a quote or order creates a single quote line item (QLI) or order item (OI) per asset transaction. The create order process resets the ASP timeline to reflect the new transaction through the end of the subscription period.

For the account that you want to change, go to the Assets tab and open the Managed Assets viewer.
Select the assets and click Amend, Renew, or Cancel.
Enter the date for the change to take effect.
You can select a date before the start date of an existing future ASP.
Click Create Order, and then click Create Single Order.
Select the new order, activate it, and set the status to complete.
Future-Dated Amendment Types and Results
Familiarize yourself with the various types of future-dated amendments and their impact on your asset records. Understanding these behaviors ensures that you accurately manage upsells, reductions, and attribute changes within your asset lifecycle.
Honor Precise Time Zones in Asset Lifecycle Start and End Dates
Specify exact time zone precision for asset lifecycle start and end dates to meet detailed contract requirements and manage complex global subscriptions. Time resolution makes sure that asset state periods (ASPs) and subsequent amendments start and end exactly as specified, providing parity for noncontiguous changes.
