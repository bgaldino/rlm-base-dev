---
article_id: ind.qocal_ramp_deal_for_groups_manage.htm
title: Actions for Managing a Ramp Deal for Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deal_for_groups_manage.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Actions for Managing a Ramp Deal for Groups

After you create a group ramp schedule, perform these actions to manage segments and lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
ACTION	ACTION SCOPE	DESCRIPTION
Browse Catalogs	Segment-Level	

Adds products to group ramp segments. You can add the products to the current segment or the current and subsequent segments in the ramp schedule group.

If you use the Browse Catalogs quick action at the quote or order level to add products, they’re added only to the first group as nonramped lines.


Clone Segment	Segment-Level	Creates the next segment by copying lines and updating the start and end dates for the new segment. You can copy only the ramped lines or all the lines.
Delete Segment	Segment-Level	

Deletes a segment and all the lines in it. You can delete segments only from the start or end of a schedule.

You can’t use the Bulk Delete option on a quote or order that contains a group ramp schedule.


Remove from Schedule	Segment-Level	Removes the segment from the group ramp schedule and converts all the lines within the segment to nonramped lines. You can remove segments only from the start or end of a schedule.
Edit Ramp Schedule	Schedule-Level or Segment-Level	

Shows options to edit the names, start dates, and end dates of segments. If you change a segment’s start and end dates, Transaction Management automatically updates the dates of all the line items within the segment.

If your admin turns on only Ramp Deals for Groups in Quotes and Orders, this action is available at the segment level.

If your admin turns on both the Ramp Deals for Groups in Quotes setting and the Orders and Multiple Ramp Schedules Per Transaction setting, this action is available at the schedule level.


View Past Segments	Schedule-Level	

Shows a summary of the segments that are in the past.

This action is available only on auto-generated asset ramp schedules in amendment transactions that you create after your admin turns on the Multiple Ramp Schedules Per Transaction setting.


View Ramp Details	Line-Level	

Shows a summary of a ramped line, including its quantity, price, and dates across all the segments that it’s part of.

You can view ramp details only for ramped line items.


Delete	Line-Level	

Deletes a line item and all its related ramped line items in the subsequent segments.

If you add the same product back to a ramp segment, the product is treated as a separate line and a new asset is created for it.

To learn how configuration works for products in group ramp segments, see Considerations for Configuring Products with Ramp Deals.

To learn how to manage usage products in group ramp segments, see Ramp Deals for Groups for Usage Products.
