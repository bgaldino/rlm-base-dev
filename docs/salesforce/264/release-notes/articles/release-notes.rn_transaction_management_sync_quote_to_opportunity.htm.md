---
article_id: release-notes.rn_transaction_management_sync_quote_to_opportunity.htm
title: Sync Quote to Opportunity
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_sync_quote_to_opportunity.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_transaction_management.htm
fetched_at: 2026-09-30
---

# Sync Quote to Opportunity

Sync a quote's line items to its associated opportunity's line items when reps add, update, or delete items on the quote. This runs the sync in the background and returns a tracking ID so you can monitor its progress, and returns an error if the quote isn't associated with an opportunity. The capability to sync quote and opportunity line items helps keep opportunity records accurate as quotes change and reduces the manual effort required by sales reps to update opportunity line items themselves.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

How: To sync a quote's line items to its opportunity, use the Sync Quote to Opportunity action. From Setup, in the Quick Find box, find and select Revenue Settings. Turn on Asynchronous Opportunity Sync. Then create a flow that triggers when you want the sync to run, checking the quote's IsSyncing field before invoking the Sync Quote to Opportunity action, which can also be triggered manually or via Apex.

SEE ALSO
Salesforce Help: Set Up Background Opportunity Sync
