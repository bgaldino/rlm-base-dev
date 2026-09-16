---
article_id: ind.qocal_action_button_group_important_considerations.htm
title: Action Button Group Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_action_button_group_important_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_configure_placement_of_action_buttons.htm
fetched_at: 2026-09-04
---

# Action Button Group Considerations

Learn how action button groups behave in the Transaction Line Editor (TLE) and Sales Transaction Line Editor (STLE) to design an efficient experience for your sales team.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled

Keep these requirements and system limits in mind when configuring your button layouts.

Salesforce uses the default action button configuration until you configure a custom one. After you define a custom layout, the system uses that configuration instead.
If you don't specify which actions appear or how they're arranged, the editor shows the default actions divided into four groups. The first three groups contain a single action each: QuoteAdjustment, AddAssets, and ImportQuoteLineItems. The last group contains the remaining actions, with only four visible.
You can’t include Salesforce admin-created custom actions at the header or row level. Only standard, built-in STLE actions are available in the action picker.
You can drag actions to reorder them within a group, but you can't drag entire button groups into a different order.
Each action can belong to only 1 button group at a time.
You can create up to 10 button groups, with each group having up to 10 actions. Only the first 10 actions appear on the STLE header at run time. The more button groups you add, the fewer buttons are visible.
