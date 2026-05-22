---
article_id: ind.qocal_set_up_ramp_deals_for_groups.htm
title: Set Up Ramp Deals for Groups in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_ramp_deals_for_groups.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Set Up Ramp Deals for Groups in Agentforce Revenue Management

To make it easier for sales reps to break down complex, long-term deals for multiple products into smaller, time-based segments, turn on Ramp Deals for Groups in Quotes and Orders. So users can create multiple ramp schedules with different segment types and dates in a single transaction, turn on Multiple Ramp Schedules Per Transaction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To turn on the Ramp Deal for Groups in Quotes and Orders setting:	Customize Application

Before you turn on the setting, complete these prerequisites.

If you created a custom Product Discovery flow before Winter ’25, clone the latest prebuilt Discover Products flow and customize it.
If you customized the Transaction Management pricing procedure before Winter ’25, clone the latest prebuilt Revenue Management Default Pricing Procedure and customize it.
NOTE Don’t change the name of the Uplift formula-based pricing component. If you change the name, the uplift is still applied, but the price waterfall doesn’t show the uplift value.
If you customized Product Configurator flows before Winter ’25, clone the Default Product Configurator Flow and customize it.
Turn on the Enable Groups in Quotes and Orders and the Clone Quotes and Orders settings. See Enable Revenue Settings.

Perform these steps to turn on the setting.

In Setup, find and select Revenue Settings.
Turn on Ramp Deals for Groups in Quotes and Orders.
After you turn on the setting, users can create only 1 ramp schedule per quote or order.
If necessary, turn on Multiple Ramp Schedules Per Transaction.
IMPORTANT

Orders containing group ramp schedules that were created after turning on Ramp Deals for Groups in Quotes and Orders but before turning on Multiple Ramp Schedules Per Transaction can’t be activated.

To resolve this limitation, create a migration script that creates a group ramp schedule and moves the existing segments into it for all quotes and orders.

After you turn on the setting, complete these steps.

Add the Sales Transaction Line Editor component to quote and order page layouts.
IMPORTANT The Transaction Line Editor component doesn’t support ramp deals for groups.
Configure Sales Transaction Line Editor.
Select Show side panel when users click a record.
Use the Display Columns setting to show these quote line item and order product fields.
Start Date
End Date
Segment Type
NOTE To easily identify ramped lines during testing, you can also show the Ramp Identifier and Segment Identifier fields. Transaction Management populates the values in these fields for all ramped lines.
Use the Display Columns setting to show these quote line group and order product group fields.
End Date
Is Ramped
On quote page layouts, Quote Line Group Name. On order page layouts, Order Product Group Name.
Segment Type
Start Date
NOTE The product and group names must appear in the first column. On quote page layouts, move the [Product] Product Name and [Quote Line Group] Quote Line Group Name fields to the top of the Selected list. Similarly, on order page layouts, move the [Product] Product Name and [Order Product Group] Order Product Group Name fields to the top of the Selected list.
To use unit price uplifts, show the Unit Price Uplift field.
If necessary, change the fields that must appear in the View Ramp Details and the Edit Ramp Schedule windows. Use the Select fields to display in the Edit Ramp Schedule window and the Select fields to display in the View Ramp Details window settings.
To test your changes, create a quote or an order with ramp deals for groups.
