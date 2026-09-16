---
article_id: ind.qocal_ramp_deal_for_groups_create.htm
title: Create a Ramp Deal for Groups with Single Ramp Schedule Per Transaction
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deal_for_groups_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_for_groups_considerations.htm
fetched_at: 2026-09-04
---

# Create a Ramp Deal for Groups with Single Ramp Schedule Per Transaction

Turn on only Ramp Deals for Groups in Quotes and Orders to treat the entire transaction automatically as a single implicit ramp schedule.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To manage ramp deals for quote line item groups:	Create on Quotes
To manage ramp deals for order product groups:	Create on Orders
Open a quote or order and click Add Group.
Click the group name to open the side panel.
Enter start and end dates. For a Yearly segment type, set the duration to exactly 365 days.
Turn on Is Ramped. Always use the side panel—don't use the group record page.
Select a segment type as Yearly (exactly 365 days for all segments, fixed) or Custom (flexible duration).
Save your changes.
Transaction Management creates a ramp schedule and converts the group into the first segment.
To add subsequent segments, click Show more actions on the last segment and select Clone Segment.
Use Edit Ramp Schedule on an initial sale quote or an amended quote to rename segments, adjust dates, and change segment types.
