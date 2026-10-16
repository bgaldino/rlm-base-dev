---
article_id: ind.qocal_auto_refresh_stle_transaction_summary_considerations.htm
title: Sales Transaction Line Editor and Transaction Summary Auto-Refresh Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_auto_refresh_stle_transaction_summary_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_auto_refresh_stle_transaction_summary_help.htm
fetched_at: 2026-09-04
---

# Sales Transaction Line Editor and Transaction Summary Auto-Refresh Considerations

Auto-refresh keeps data up to date across the Transaction Line Editor (TLE), Sales Transaction Line Editor (STLE), and Transaction Summary as sales reps make changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

Review these considerations and limitations before configuring or enabling auto-refresh.

Auto-refresh only applies to changes made by the currently active sales rep's actions. If another user changes the same quote or order while it’s open, the active sales rep's view doesn't auto-refresh. To include those changes, select Refresh from the dropdown menu.
Turn on Change Data Capture for auto-refresh to work on both quotes and orders. Turning on only one object limits auto-refresh to that object type. Changes to quote line item, order item, quote line group, order line group, quote line detail, and order line detail refresh too.
