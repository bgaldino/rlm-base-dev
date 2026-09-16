---
article_id: ind.qocal_auto_refresh_stle_transaction_summary_help.htm
title: Turn On Auto-Refresh for the Sales Transaction Line Editor and Transaction Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_auto_refresh_stle_transaction_summary_help.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_customize_transaction_line_editor.htm
fetched_at: 2026-09-04
---

# Turn On Auto-Refresh for the Sales Transaction Line Editor and Transaction Summary

Keep your sales reps focused on closing deals instead of reloading pages. To turn on auto-refresh for Sales Transaction Line Editor (STLE) and Transaction Summary, set up Change Data Capture for the quote and order objects. The auto-refresh feature captures changes made outside STLE, including record pages, flows, Apex triggers, and Agentforce actions. After it's turned on, sales reps see accurate line items right away, helping them work with confidence and complete quotes and orders faster.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.

Suppose a server-side process, such as an Apex trigger, an auto-launched or record-triggered flow, or an Agentforce action, updates a quote or order. STLE and the Transaction Summary automatically reflect the updated line items. You don't reload the browser to see the latest data.

Auto-refresh delivers value to your sales team in a few key ways.

Users see updated line items the moment that their automation changes a quote or order, which reduces errors and can speed up a deal.
Apex triggers, flows, and Agentforce actions benefit automatically. You don't change any code after you complete the one-time setup. There’s no disruption to existing automation.
The Refresh option in the dropdown menu reloads the STLE data, so users can use it to pull in any change that isn't auto-refreshed, such as an edit made by another user.
Auto-refresh uses the same access that grants use of the STLE. This feature doesn't introduce a new permission or permission set.

A Salesforce admin completes these steps.

From Setup, in the Quick Find box, enter Change Data Capture, and then select Change Data Capture.
In the Available Entities list, select Quote, and then click the arrow to move it to Selected Entities.
Select Order, and then move it to Selected Entities.
Select both quote and order for full coverage. If you turn on only one object, then auto-refresh works only for that object type.
Save your changes.

The next time a user opens a quote or order in the Sales Transaction Line Editor, auto-refresh is active.

IMPORTANT You don't turn on Change Data Capture on child objects. Turning on the quote and order objects covers edits to a quote or order and to its line items, line groups, and line-item attributes.

Only the user who triggers the change sees the auto-refresh. When a rep runs the flow, trigger, or agent action, that rep's STLE refreshes. If another user changes the same quote or order while a rep has it open, then the rep's STLE doesn't auto-refresh. The rep selects Refresh from the dropdown menu to pull in those changes.

If a refresh arrives and the user has no unsaved edits, STLE refetches the data quietly and shows the update after a brief loading state. When the user has unsaved edits, the STLE shows a prompt with these options.

Save: Save the pending edits, and then refresh the data.
Discard: Revert the pending edits, and then refresh the data.
Cancel: Keep the pending edits and don't refresh.

When a sales rep is mid-edit or a save is still processing, STLE holds incoming changes. The existing save or discard flow resolves the sales rep's unsaved edits.

The transaction summary refreshes the same way. Because it's read-only, it refreshes the data without a save or discard prompt.

Sales Transaction Line Editor and Transaction Summary Auto-Refresh Considerations
Auto-refresh keeps data up to date across the Transaction Line Editor (TLE), Sales Transaction Line Editor (STLE), and Transaction Summary as sales reps make changes.
