---
article_id: ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm
title: Create Ramp Deals for Groups with Multiple Ramp Schedules Per Transaction
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals_groups_create_multiple_ramp_schedules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Create Ramp Deals for Groups with Multiple Ramp Schedules Per Transaction

If your admin turned on the Multiple Ramp Schedules Per Transaction setting, create a ramp schedule for each ramp deal. To create one, create a group ramp schedule and then add group ramp segments to it. Next, add products to the segments. Then, edit the lines to change quantity, discounts, and configurations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To manage ramp deals for quote line item groups:	Create on Quotes
To manage ramp deals for order product groups:	Create on Orders

If your admin turns on only the Ramp Deals for Groups in Quotes and Orders setting, see Create Ramp Deals for Groups with Single Ramp Schedule Per Transaction.

Create a Ramp Deal Structure

A ramp deal structure consists of a group ramp schedule and its related ramp segments. A ramp schedule organizes related ramp segments and defines the type of segments, Custom or Yearly. A segment contains products and specifies their time period.

Open a quote or an order record.
Create a ramp schedule group.
Click Add Group.
Save your changes.
Click the group name.
In the side panel, for Quote Line Group Type, select Ramp Schedule Group.
Save your changes.
Create a group ramp segment in the schedule.
Click  corresponding to the schedule, and then click Add Sub Group.
Save your changes.
Click the name of the subgroup.
Enter the start and end dates.
To create a segment of the type Yearly, set the duration to exactly 365 days.
Turn on Is Ramped.
Use only the side panel to turn on the Is Ramped setting. Don’t use group record pages.
Transaction Management converts the group into a group ramp segment.
Select a segment type.
If you want segment duration to be exactly 365 days for all the segments in the schedule, select Yearly. You can’t edit the segment type later.
Save your changes.
For each additional segment that you want to add, click  corresponding to the last segment in the schedule, and then select Clone Segment.
Fine-tune your ramp schedule.
Click  corresponding to the schedule, and then select Edit Ramp Schedule.
Edit the segment names to meet your requirements.
If needed, edit the segment dates.
EXAMPLE
Add Products to the Ramp Deal

After you create a ramp deal structure, add products to segments. You can add products to a single segment or to a segment and all subsequent segments.

Click  corresponding to a segment, and then click Browse Catalogs.
Select a catalog, and then click Next.
Add products, and then click Next.
Select the group ramp segments that you want to add products to.
Current Segment Only: Adds products as nonramped lines
Current and Subsequent Segments: Adds rampable products as ramped lines and other products as nonramped lines
You see the options to select segments only after your admin configures the Discover Products flow. See Set Up Ramp Deals for Groups in Agentforce Revenue Management.
Update Product and Ramp Details

After you add products to create lines, edit lines to specify details, such as quantities, discounts, and configurations. You can also view details and manage the lines by using schedule-level, segment-level, and line-level actions.

Update lines to specify quantities and discounts.
See View and Edit Quotes and View and Edit Orders.
Configure your lines. See Configure Products with the Product Configurator and Considerations for Configuring Products with Ramp Deals.
Configuration changes are propagated only after your admin configures the Product Configurator flows. See Set Up Ramp Deals for Groups in Agentforce Revenue Management.
Use the schedule-level, segment-level, and line-level actions to fine-tune the ramp deal.
