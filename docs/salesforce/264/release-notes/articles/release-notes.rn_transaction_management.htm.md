---
article_id: release-notes.rn_transaction_management.htm
title: Transaction Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Transaction Management

Improve flexibility and productivity when managing quotes, orders, and asset lifecycle changes. Configure procedure plans for specific industries, backdate asset transactions, maintain time zone accuracy throughout the asset lifecycle, and update prices through price amendments. Work more efficiently in Sales Transaction Line Editor with enhanced filtering, automatic refresh, and configurable action buttons. Tailor transaction pages with Dynamic Forms.

Limit a Procedure Plan to a Specific Industry
Prevent pricing errors when you have multiple industries in a single org by defining which industry or vertical the procedure plan applies to. Use the new Subtype field to make sure that your plan shows only the pricing procedures matching the specific subtype. Then, when you configure a Life Sciences or Commerce procedure plan, you can add only pricing procedures intended for the selected industry or vertical.
Gain Transaction Flexibility with Backdated Asset Changes
Your sales reps can now apply past effective dates to amendment, cancellation, and renewal transactions for standard and ramped assets. They can also apply past effective dates to transfer and swap transactions for standard assets. Backdated asset transactions keep contract terms, billing schedules, and invoices aligned with the intended effective dates.
Maintain Time Zone Accuracy for Asset Lifecycle Changes
Time Zone is now stored on the asset and populated to amendment, renewal, and cancellation transactions. Start and end dates remain consistent with the asset's original local time zone, so sales reps can manage subscriptions across different time zones without manual time zone conversions.
Gain Pricing Flexibility with Price Amendments
Your sales reps can now use price amendments to update the sales price on quote lines or the unit price on order lines without modifying quantities, attributes, or bundle configurations. Updated prices are reflected throughout the standard order and billing processes.
Accelerate Transaction Updates with Advanced Filters
Your sales reps can now use advanced filters to quickly isolate quote and order lines by product name, custom fields, and fields on related records. Focus updates on relevant lines in complex transactions to save time, reduce rework, and improve accuracy when updating pricing and terms.
Edit Accurate Quotes and Orders in Sales Transaction Line Editor with Autorefresh
Sales Transaction Line Editor (STLE) and Transaction Summary now refresh automatically when a custom flow, Apex trigger, or Agentforce action changes the quote or order your sales reps are viewing. Sales reps see the latest line items without reloading the page manually, so their work on quotes and orders always reflects the most current data. The Refresh tab now reliably reloads the STLE data.
Organize Sales Transaction Line Editor Actions into Button Groups for Efficient Editing
Configure Sales Transaction Line Editor (STLE) header actions with a new, visual admin UI instead of a text box. Organize actions into button groups, set how many actions show in each group, and add as many groups as your business needs. Ten action groups are visible, with the remaining groups placed in an overflow menu. Existing text box configurations carry over automatically, keeping your sales reps' experience the same until you're ready to reorganize.
Build Focused Quote Line Item and Order Product Pages with Dynamic Forms
Tailor what users see on quote line item and order product records by upgrading their Lightning pages to Dynamic Forms. Place individual fields and field sections anywhere on the page, and set visibility rules so that users see only the fields relevant to their transaction. Previously, these two objects supported page layouts only.
Sync Quote to Opportunity
Sync a quote's line items to its associated opportunity's line items when reps add, update, or delete items on the quote. This runs the sync in the background and returns a tracking ID so you can monitor its progress, and returns an error if the quote isn't associated with an opportunity. The capability to sync quote and opportunity line items helps keep opportunity records accurate as quotes change and reduces the manual effort required by sales reps to update opportunity line items themselves.
Changed Connect REST API in Transaction Management
Use the enhanced Read Sales Transaction API to discover available batches, then retrieve only the batches that you need in parallel.
New Invocable Action in Transaction Management
Keep forecasts up to date by syncing quote line items to opportunity line items so that your sales teams get consistent data with less manual effort. Changes to quote line items update the matching opportunity line items, but not the reverse. To use this action in a flow or other automation, turn on Asynchronous Opportunity Sync in Revenue Settings.
