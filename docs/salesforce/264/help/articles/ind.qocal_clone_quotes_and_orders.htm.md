---
article_id: ind.qocal_clone_quotes_and_orders.htm
title: Clone Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_clone_quotes_and_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_sales_transactions_rev_cloud.htm
fetched_at: 2026-09-04
---

# Clone Quotes and Orders

Duplicate quotes or orders along with their associated line items and groups to save time and ensure data consistency. Cloning reduces manual entry errors by creating an exact draft replica of a source record while leaving the original unchanged.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To edit a page layout:	Customize Application

The cloning process copies the complete transaction structure, including field values, related records from standard and custom objects, product configurations such as bundles, standalone lines, grouped lines, and associated actions for quote line items and order products.

When you clone transactions with group ramp schedules, the cloned transaction preserves the original schedule structure. Amendment and renewal quotes with ramp schedules also preserve ramp and segment relationships after cloning.

For complex transactions, the process also duplicates group structures and clones amendment, renewal, and cancellation quotes.

Set Up Clone Quotes and Orders

When you turn on Clone Quotes and Orders on the Revenue Settings page, it reflects as the Deep Clone action on the quote or order record page.

From Setup, in the Quick Find box, search for and select Revenue Settings.
Turn on Clone Quotes and Orders.
NOTE This setting only controls user interface actions. The Clone Sales Transaction API supports cloning even when this setting is off.
Add the Deep Clone Action to Page Layouts

Add the Deep Clone action to page layouts to make the feature accessible on record pages.

From Setup, select Object Manager.
Select the Quote or Order object.
Click Page Layouts, select the specific layout to modify, and click Edit.
Select Mobile & Lightning Actions in the palette.
Drag the Deep Clone action into the Salesforce Mobile and Lightning Experience Actions section.
Save the layout.
Clone a Transaction

Clone an entire quote or order to create a duplicate of a transaction. Cloned quotes and orders are created in Draft status. Approval work items aren't copied to the cloned transaction.

Open a quote or order record.
Select Deep Clone from the dropdown menu.
Confirm the action.
NOTE
You can clone up to 6,000 records per transaction. For transactions with more than 1,000 lines, contact your Salesforce account executive to increase the limit.
Cloning quotes or orders using the Deep Clone action, Clone Sales Transaction API, or Deep Clone Sales Transaction invocable action doesn’t support the ISCLONE() formula function.
To clone custom objects and custom fields, configure the context definition for the sales transaction. For custom child objects, map the ParentReference field to the parent record ID.
Clone Lines or Groups

Duplicate individual components within a transaction by cloning specific line items or groups.

Open the quote or order record.
Select the component to copy.
To duplicate a line item, select the item and click Clone.
To duplicate a group, select the group and click Clone Group.
Review the duplicated data.
Line item clones include configurations, field values, and related records.
Bundle clones include the entire structure and all child line items.
Group clones include the group and every line item inside it.
