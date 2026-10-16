---
article_id: release-notes.rn_transaction_management_stle_enhance_autorefresh.htm
title: Edit Accurate Quotes and Orders in Sales Transaction Line Editor with Autorefresh
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_transaction_management_stle_enhance_autorefresh.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_transaction_management.htm
fetched_at: 2026-09-30
---

# Edit Accurate Quotes and Orders in Sales Transaction Line Editor with Autorefresh

Sales Transaction Line Editor (STLE) and Transaction Summary now refresh automatically when a custom flow, Apex trigger, or Agentforce action changes the quote or order your sales reps are viewing. Sales reps see the latest line items without reloading the page manually, so their work on quotes and orders always reflects the most current data. The Refresh tab now reliably reloads the STLE data.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

Why: A record-triggered flow updates quote lines after a pricing recalculation. An Apex trigger updates order lines after an external system callback. An Agentforce action runs Apex that changes quote lines. Previously, sales reps reloaded the entire browser page to see those changes in STLE or Transaction Summary. Now, when a rep's own automation changes the quote or order they're viewing, the STLE and Transaction Summary pick up the change automatically. Sales reps stay focused on the deal instead of the browser tab. This update doesn’t require changes to existing Apex or flows.

The auto-refresh also accounts for work in progress. If a sales rep has unsaved edits when a refresh happens, the STLE prompts them to save, discard, or cancel before applying the update. The refresh doesn’t overwrite the work. While they’re actively editing or a save is pending, the STLE holds incoming updates until that action finishes, so they aren’t interrupted mid-keystroke or before saving.

How: From Setup, in the Quick Find box, enter Change Data Capture, and then select Change Data Capture. In the Available Entities list, select Quote and Order, move them to Selected Entities, and save your changes. This one-time, per-org setup doesn't add a new permission or permission set, and existing access to STLE carries over.

SEE ALSO
Change Data Capture
