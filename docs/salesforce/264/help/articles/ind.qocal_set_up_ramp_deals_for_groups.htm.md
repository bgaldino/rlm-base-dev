---
article_id: ind.qocal_set_up_ramp_deals_for_groups.htm
title: "Prerequisites: Ramp Deals for Groups"
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_ramp_deals_for_groups.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.setting_up_ramp_deals.htm
fetched_at: 2026-09-04
---

# Prerequisites: Ramp Deals for Groups

Complete these essential setup steps before configuring your highly recommended group-based ramp deals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To turn on the Ramp Deal for Groups in Quotes and Orders setting:	Customize Application
In Setup, find and select Revenue Settings. Turn on both the Enable Groups in Quotes and Orders and the Clone Quotes and Orders settings.
Update your custom flows.
If you created a custom Product Discovery flow before Winter '25, clone the latest prebuilt Discover Products flow and customize it.
If you customized the Transaction Management pricing procedure before Winter '25, clone the latest prebuilt Revenue Management Default Pricing Procedure and customize it.
If you customized Product Configurator flows before Winter '25, clone the Default Product Configurator Flow and customize it.
In Setup, find and select Revenue Settings. Turn on Ramp Deals for Groups in Quotes and Orders.
Turn on Multiple Ramp Schedules Per Transaction.
Sales reps can create up to 10 separate ramp schedules within a single quote or order. If you turn on this setting after ramp deals for groups are active, Transaction Management can't activate orders created between the two activations. Use a migration script to resolve those orders.
If your org uses a custom Discover Products flow and you want to enable upgraded group ramp support, complete these steps.
From Setup, in the Quick Find box, enter Flows and select it.
Open the custom Discover Products flow.
Rearrange the nodes in the Discover Products flow.
In your custom Discover Products flow, move the Ramped Group node so that it appears after the catalog selection node, and before the Product List node.
Configure the Select Ramp Segments node.
Click the Select Ramp Segments node.
Click the node again to open its settings.
In Advanced, set the Discover Products context output variable.
Save the node.
Update the Product List node settings.
Click the Product List node.
In Advanced, locate the Revisited Screen Values field.
Change the value from Use values from when the user last visited this screen to Refresh inputs to incorporate changes elsewhere in the flow.
Save the node.
For instructions, see Override Flow for Product Discovery.
Add the Sales Transaction Line Editor component to quote and order page layouts.
NOTE The legacy Transaction Line Editor component doesn't support ramp deals for groups. Use the Sales Transaction Line Editor.

Configure the Sales Transaction Line Editor to show these fields:

RECORD TYPE	FIELDS TO SHOW
Quote line items and order products	
Start Date
End Date
Segment Type

To identify ramped lines during testing, also show:

Ramp Identifier
Segment Identifier

Quote line groups and order product groups	
Start Date
End Date
Segment Type
Is Ramped
Quote Line Group Name or Order Product Group Name

Product and group name fields appear in the first column.


Uplifts (optional)	Add Unit Price Uplift
Edit Ramp Schedule and View Ramp Details windows (optional)	Configure which fields appear in these windows.
During debugging or setup	

Add the Ramp Identifier column to make debugging easier.

You can remove this field once you move to production.

IMPORTANT Don't rename the Uplift formula-based pricing component. Renaming it causes the system to apply the uplift without showing the value in the price waterfall.
