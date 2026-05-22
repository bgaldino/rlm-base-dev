---
article_id: ind.um_track_usage_with_unified_dashboard.htm
title: Track Usage Components with Unified Usage Dashboard
source_url: https://help.salesforce.com/s/articleView?id=ind.um_track_usage_with_unified_dashboard.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Track Usage Components with Unified Usage Dashboard

After an order is activated, assetized, and entitlements are granted, you can use the dashboard to track wallet balances, monitor overages, and verify applicable rates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To access the unified usage dashboard:	Usage Management Run Time User

Before you access the unified dashboard, make sure that you’ve completed these prerequisites.

Select the latest Rating Discovery Procedure in Revenue Settings.
Add Usage Component to the Record Pages.
SEE ALSO
Grant Binding
Anchor Products with Packs
Access the Unified Usage Dashboard

Go to the usage dashboard and review the individual tabs for usage details, grants, and policies.

From the App Launcher, find and select the Usage Management App.
To view the dashboard, go to the relevant account page for pooled resources, or an asset page for independent resources.
Click Usage Details.
The Usage Details tab lists all assets that are bound to the account, such as assets, contracts, or any custom object.
To view the grants available for each resource, click Grants.
The Grants tab lists all associated grants with details, such as the associated product and the rollover and refresh policies, with the effective period dates.
To view the policies that govern the usage resources, click Policies.
The Policies tab shows a centralized list of the governing policies created for the target, such as aggregation policies, rating frequency policies, and overage policies.
View Applicable Rates

When a customer has multiple assets bound to the same account, such as a standard anchor product and an add-on pack with different rates and validity periods, Consumption Management automatically identifies and shows the winning rate. The proration engine evaluates these varying validity periods and shows you the currently applicable net unit rate.

On the Account page, click Rates.
The Rates section shows the finalized, winning rates for any consumption on the account or asset. This tab ensures that you’re viewing the net rate the rating engine uses for rate calculations. For example, a newer add-on pack rate takes precedence over an older anchor rate until the pack expires.
To view the specific negotiated rate for an individual asset, go to that asset record page, and then click Rates.
Monitor Wallet Balances

Track how many grants have the customer consumed and what remains available.

On the Account page, click Wallets.
The Wallet tab shows digital wallets that represent parent buckets created for the resources, such as data, calls, and compute time. The visual indicators show the percentage of resources consumed.
To open the parent Usage Entitlement Bucket record associated with the wallet, click View Details.
The record shows the aggregated balance of all associated grants in the Total Age of Balance field.
To view child buckets associated with the parent bucket, click Related in the Usage Entitlement Bucket record.
The Related tab shows child buckets under the Usage Entitlement Bucket section with the balances for individual purchases or add-on packs.
To review the detailed audit trail for either a parent or child bucket, click Wallet Statement in the Usage Entitlement Bucket record.
The Wallet Statement tab provides a chronological log of all credit entries and debit entries.
