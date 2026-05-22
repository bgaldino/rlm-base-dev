---
article_id: ind.qocal_split_quote_into_multiple_orders.htm
title: Split Quotes into Multiple Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_split_quote_into_multiple_orders.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Split Quotes into Multiple Orders

Unlock greater flexibility in your sales process by creating multiple, independent orders from a single quote. Segmenting a quote helps streamline downstream operations, such as fulfillment, billing, and invoicing. For example, create separate orders by using quote groups or quote line fields like shipping locations, recipients, or start dates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create orders from quotes:	

Create Orders from Quotes permission

AND

Product Catalog Management Viewer permission set

Prerequisites for Splitting Quotes

Perform these tasks before splitting a quote into multiple orders.

In Setup, find and select Revenue Settings.
Turn on Advanced Order Creation From Quote.
This action updates the functionality of the Create Order button on quotes.
NOTE Changes take effect after approximately 10 minutes. Log out and log back in to apply changes immediately.
In Setup, find and select Flows, and select the Create Orders From Quote flow template.
Enter a unique flow label and API name and save it as a new flow.
Configure the Order Creation method, Split field, and other elements by customizing the flow pages.
Save and activate the flow.
In Setup, find and select Revenue Settings.
Add the API name of your new flow to the Set Up Flow for Creating Orders from Quotes setting.
Save your changes.
Create Multiple Orders from a Quote

Segment a quote into multiple orders based on specific fields or groups.

From App Launcher, search for and select Quotes.
Select a quote and then click Create Order.
Select an order creation option.
Create Single Order: Creates one order.
Create Order by Group: Creates orders based on a quote line item group.
Create Order by Field: Creates orders based on a quote line item field, such as location or delivery date.
If you select the Create Order by Field option, enter a field name like Start Date in the Quote Line Item Field search and click Finish.
Click View the new Orders from the confirmation message.
New orders appear in the list view with a Draft status.
Update the new orders and save your changes.
Lightning App Builder shows supported standard fields during design time.
Supported data types for custom fields include Checkbox, Date, Text, Email, URL, Phone, Picklist, Multi-select Picklist, Foreign Key, Foreign Key + Option, and External Lookup.
