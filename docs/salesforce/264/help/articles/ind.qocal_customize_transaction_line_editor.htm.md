---
article_id: ind.qocal_customize_transaction_line_editor.htm
title: Add and Customize the Transaction Line Editor or Sales Transaction Line Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_customize_transaction_line_editor.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_set_up_quote_and_order_features_in_revenue_cloud.htm
fetched_at: 2026-09-04
---

# Add and Customize the Transaction Line Editor or Sales Transaction Line Editor

To help sales reps to view and manage quote and order line items efficiently, add the Transaction Line Editor or Sales Transaction Line Editor (STLE) to the page layout and customize the fields that the editor shows. We strongly recommend using STLE because its streamlined, single-grid layout improves performance at scale and provides access to the latest capabilities in Transaction Management. The Transaction Line Editor remains available, but it’s no longer being enhanced.

The Sales Transaction Line Editor helps:

Organize quotes and orders by using nested groups and group ramps.
Perform bulk actions such as editing fields, updating discounts, or deleting selected line items or groups.
Filter and sort items across groups.
View and edit group details in the side panel.

The line editors show as Quote Line Items on the Quote page and as Order Products on the Order page. To access this component, users need an Revenue Management permission set, such as Assetize Order or Price and Tax Calculation for Quoting.

The line editors use the Transaction Line Progress Indicator component to:

Show the progress of line item additions and changes.
Show informational and error messages.
Support the browse catalogs functionality.

After you add a line editor to the page layout, add the Transaction Line Progress Indicator component. For more context about the Transaction Line Progress Indicator, see Transaction Line Progress Indicator Component.

Add the component to a quote or order page.
From Setup, in the Quick Find box, enter Lightning App Builder, and then select Lightning App Builder.
For Quote Record Page, click Edit.
Click the Tabs component.
NOTE We recommend that you add the Transaction Line Editor or Sales Transaction Line Editor to the default tab on quote or order record pages. This addition makes sure that the editor loads along with the page, rather than only when you switch to another tab.
In the Tabs component's Page panel, click Add Tab.
In the Page panel, click the tab item that you added, and then select Lines as the tab label.
On the canvas, click the Lines tab.
Drag the Transaction Line Editor or Sales Transaction Line Editor component to the tab.
Drag the Transaction Line Progress Indicator component above the line editor.
Customize the line editor component.
Highlight the component.
Under Display Columns, click Select....
Select the columns (fields) that you want to show on the line editor. See Select Fields for the Line Editor.
If needed, select the Show product quick add and the Show side panel when users click a record link options.
To show fields on the side panel, move the fields to the Selected section and arrange them in your preferred order.

The side panel shows up to 200 product attributes for each quote line, sorted alphabetically by their definition name. It shows only attributes that aren't marked hidden in Product Catalog Management. See Working with Product Attribute Fields.

If you're using STLE and ramp deals for groups, select fields to display in the View Ramp Details and Edit Ramp Schedule window.
Save your changes.
Activate the page and select a form factor.

You can further customize the page to set the placement and sequence of the action buttons. See Configure the Placement and Sequence of Action Buttons in Line Editor.

Select Fields for the Line Editor
Select line-level fields, group fields, and related record fields in the Display Columns to manage which fields appear in the line editor.
Adjustment Type Column
The Adjustment Type column merges multiple adjustment fields into a single column so that sales reps can make pricing adjustments more efficiently.
Turn On Auto-Refresh for the Sales Transaction Line Editor and Transaction Summary
Keep your sales reps focused on closing deals instead of reloading pages. To turn on auto-refresh for Sales Transaction Line Editor (STLE) and Transaction Summary, set up Change Data Capture for the quote and order objects. The auto-refresh feature captures changes made outside STLE, including record pages, flows, Apex triggers, and Agentforce actions. After it's turned on, sales reps see accurate line items right away, helping them work with confidence and complete quotes and orders faster.
