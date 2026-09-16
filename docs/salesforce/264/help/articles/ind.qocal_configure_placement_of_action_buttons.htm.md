---
article_id: ind.qocal_configure_placement_of_action_buttons.htm
title: Configure Header-Level Action Buttons in Sales Transaction Line Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_configure_placement_of_action_buttons.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_customize_quote_and_order_capture.htm
fetched_at: 2026-09-04
---

# Configure Header-Level Action Buttons in Sales Transaction Line Editor

To provide an intuitive experience for sales reps, you can customize the placement and sequence of action buttons in Sales Transaction Line Editor (STLE). Choose which actions appear as standalone buttons, button groups, or menu items in a dropdown list.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To customize the Transaction Line Editor or Sales Transaction Line Editor:	
Customize Application
Manage Revenue Management system permission

To view Transaction Line Editor or Sales Transaction Line Editor on the Orders page:	
Field-level security to these OrderItem fields:
ValidationResult (Read-only)
PriceWaterfallIdentifier (Read-only)
ParentOrderItemId (Read-only)
OrderActionId (Read-only)
Field-level security to these OrderItemRelationship fields.
AssociatedOrderItemPricing (Read-only)
AssociatedQuantScaleMethod (Read-only)
IMPORTANT Complete these prerequisites before you configure action buttons.
Turn on Enable Groups on the Revenue Settings page to include group-specific actions.
Turn on Header Adjustments on the Revenue Settings page to include QuoteAdjustment or OrderAdjustment actions.
Identify the exact, case-sensitive API names for the actions you want to appear.
In Lightning App Builder, open the quote or order record page and select Edit.
Select the STLE component.
In the Action Buttons field, enter the API names of the actions.
To show a single button, enter the action name on its own line. For example, enter AddGroup.
To separate multiple buttons with a divider line, enter the API names on the same line separated by a comma. For example, enter AddGroup, and Ungroup.
To nest actions as menu items under a main action button, place the secondary actions in parentheses. For example, enter MoveSelectedLines, (AddGroup), (Ungroup).
To create a standalone dropdown menu for multiple actions, enter the names in parentheses. For example, enter (AddGroup, ExpandAllGroups, CollapseAllGroups, Ungroup).
Save your changes.
Go to the quote or order record page to verify the button sequence and layout.

In Winter ’27, the STLE supports the built-in header-level actions that admins have been able to configure via the Lightning App Builder.

Set how many header-level actions are visible at run time and add button groups to organize actions specifically for your sales team. You can create up to 10 button groups, with each group having up to 10 actions. You can distribute up to 10 visible action slots across all groups. Within a group, drag actions to reorder them. The action picker lists only your available actions, so every action that you configure is available at run time.

If you don't specify which actions appear or how they're arranged, the editor shows the default actions divided into four groups. The first three groups contain a single action: QuoteAdjustment, AddAssets, and ImportQuoteLineItems. The last group contains the remaining actions, with only four visible.

Use these supported API names.

Supported Actions
ACTION API NAME	DESCRIPTION	DISPLAY LABEL	API NAME
AddAssets	Add assets to the editor.	Add Assets	AddAssets
AddGroup	Create a group of line items.	Add Group	AddGroup
Ungroup	Remove grouping from selected lines.	Ungroup	Ungroup
MoveSelectedLines	Reorganize selected lines within the editor.	Move Selected Lines	MoveSelectedLines
RepriceAll	Recalculate prices for all lines.	Reprice All	RepriceAll
BulkDelete	Delete multiple selected lines simultaneously.	Bulk Delete	BulkDelete
EstimateTaxes	Calculate tax estimates for the transaction.	Estimate Taxes	EstimateTaxes
ImportQuoteLineItems	Upload line items from an external source.	Import Lines	ImportQuoteLineItems
CreateRampSchedule	Create a ramp schedule.	Create Ramp Schedule	CreateRampSchedule
ManageHeaderAdjustment	Manage header changes.	Manage Header Adjustment	HeaderAdjustment
Action Button Group Considerations
Learn how action button groups behave in the Transaction Line Editor (TLE) and Sales Transaction Line Editor (STLE) to design an efficient experience for your sales team.
