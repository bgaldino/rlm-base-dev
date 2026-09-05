---
article_id: ind.qocal_ramp_deal_for_groups_manage.htm
title: Manage a Ramp Deal
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deal_for_groups_manage.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_complex_long_term_multiple_products.htm
fetched_at: 2026-09-04
---

# Manage a Ramp Deal

After you create a group ramp schedule, use these actions to manage segments and lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
ACTION	LEVEL	WHAT IT DOES	SUPPORTED QUOTES OR RAMP SCHEDULES
Browse Catalogs	Segment	Adds products into the current segment or all subsequent ramp schedule group segments. If you use Browse Catalogs at the quote or order level instead, products are added only to the first group as non-ramped lines.	All quote types and ramp schedules.
Clone Segment	Segment	Creates the next segment by copying lines and updating the start and end dates for the new segment. You can copy only the ramped lines or all the lines.	
Initial Sale Ramp Deal
Auto-generated ramp schedule on Amendment and Renewal Quotes

Delete Segment	Segment	Deletes a segment and all its lines. Only available at the start or end of a schedule. You can't use the Bulk Delete option on a quote or order that contains a group ramp schedule.	
Initial Sale Ramp Deal
Newly cloned segment on auto-generated ramp schedule on Amendment and Renewal Quotes

Remove from Schedule	Segment	Removes a segment from the schedule and converts its lines to non-ramped lines. Only available at the start or end of a schedule.	New ramp schedule segments
Edit Ramp Schedule	Schedule or Segment	Shows options to edit the names, start dates, and end dates of segments. If you change a segment's start and end dates, Transaction Management automatically updates the dates of all the line items within the segment. Available at the segment level when only Ramp Deals for Groups in Quotes and Orders is turned on. Available at the schedule level when both Ramp Deals for Groups in Quotes and Orders and Multiple Ramp Schedules Per Transaction are turned on.	New ramp schedule segments.
View Past Segments	Schedule	Shows a summary of segments that are in the past. Available for auto-generated asset ramp schedules in amendments created after enabling Multiple Ramp Schedules Per Transaction.	Auto-generated ramp schedule on Amendment Quotes.
View Ramp Details	Line	

Shows a summary of a ramped line, including its quantity, price, and dates across all the segments it's part of.

Available only for ramped line items.

	This ramp action is only available on ramped lines for all quote types.
Delete	Line	Deletes a line item and all its related ramped line items in subsequent segments. If you add the same product back to a ramp segment, the product is treated as a separate line and a new asset is created for it.	
New ramp schedule lines
Auto-generated ramp schedule lines on all quote types.
