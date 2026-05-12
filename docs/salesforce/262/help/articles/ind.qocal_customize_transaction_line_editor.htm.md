---
article_id: ind.qocal_customize_transaction_line_editor.htm
title: Add and Customize the Transaction Line Editor or Sales Transaction Line Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_customize_transaction_line_editor.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Add and Customize the Transaction Line Editor or Sales Transaction Line Editor

To empower sales reps to view and manage quote and order line items, add the Transaction Line Editor or Sales Transaction Line Editor to the page layout and customize the fields that the editor shows. We strongly recommend that you use the Sales Transaction Line Editor because it provides a streamlined, single-grid layout that improves performance at scale. The Transaction Line Editor remains available but is no longer being enhanced. New capabilities in Transaction Management are supported in Sales Transaction Line Editor and may not be available in Transaction Line Editor. For the best experience and access to the latest capabilities, use Sales Transaction Line Editor.

The Sales Transaction Line Editor helps you:

Organize quotes and orders using nested groups and group ramps.
Perform bulk actions such as editing fields, updating discounts, or deleting selected line items or groups.
Filter and sort items across groups.
View and edit group details in the side panel.

The line editors are shown as Quote Line Items on the Quote page and as Order Products on the Order page. To access this component, users must have any Agentforce Revenue Management permission set, such as Assetize Order or Price and Tax Calculation for Quoting.

The line editors use the Transaction Line Progress Indicator component to:

Show the progress of line item additions and changes.
Show informational and error messages.
Support the browse catalogs functionality.

So, after you add a line editor to the page layout, add the Transaction Line Progress Indicator component.

NOTE Changes to the quote header don’t appear in the Transaction Line Editor or Sales Transaction Line Editor until you refresh the page.
Add the component to a quote or order page.
From Setup, in the Quick Find box, enter Lightning App Builder, and then select Lightning App Builder.
For Quote Record Page, click Edit.
Click the Tabs component.
NOTE We recommend that you add the Transaction Line Editor or Sales Transaction Line Editor to the default tab on quote or order record pages. This makes sure that the editor loads along with the page, rather than only when you switch to another tab.
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
To show fields on the side panel, move the fields to the Selected section, and arrange them in your preferred order.

The side panel shows up to 200 product attributes for each quote line, sorted alphabetically by their definition name. Only attributes that aren’t marked as hidden in Product Catalog Management are shown. See Working with Product Attribute Fields.

If you are using Sales Transaction Line Editor and ramp deals for groups, select fields to display in the View Ramp Details and Edit Ramp Schedule window.
Save your changes.
Activate the page and select a form factor.

You can further customize the page to set the placement and sequence of the action buttons. See Configure the Placement and Sequence of Action Buttons in Line Editor.

Select Fields for the Line Editor
Select line-level fields, group fields, and related record fields in the Display Columns to manage which fields appear in the line editor.
Adjustment Type Column
The Adjustment Type column merges multiple adjustment fields into a single column so that sales reps can make pricing adjustments more efficiently.
