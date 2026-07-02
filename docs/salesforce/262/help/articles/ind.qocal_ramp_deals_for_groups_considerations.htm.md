---
article_id: ind.qocal_ramp_deals_for_groups_considerations.htm
title: Considerations for Creating Ramp Deals for Groups in Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals_for_groups_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Creating Ramp Deals for Groups in Quotes and Orders

To effectively use Ramp Deals for Groups, familiarize yourself with its product, structural, and functional aspects and limits.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Transaction Management doesn’t create ramps for all products in group ramp segments. Instead, it creates a separate asset for each quote line item for these products.
Products with One Time and Evergreen product selling models
Bundled products where the root product has the One Time or Evergreen product selling model
Bundled products, including the ones with Term-Defined product selling model, that contain a default One Time or Evergreen child product with the Proportional quantity scaling method
Derived pricing products aren’t supported, so, their prices don’t calculate correctly if you add them to a ramp deal for groups.

When Ramp Deals for Groups in Quotes and Orders is turned on and Multiple Ramp Schedules Per Transaction is turned off, you can create only 1 ramp schedule in a quote or an order.

You convert a group into a group ramp segment without explicitly creating a ramp schedule. The ramp schedule is implicit because the entire transaction is part of a single ramp schedule.

When Multiple Ramp Schedules Per Transaction is turned on, you can create up to 10 ramp schedules groups in a quote or an order.
You can create up to 12 group ramp segments in a ramp schedule.
After converting a group into a ramp segment within a schedule, you can clone the ramp segment to add more segments. You can’t convert any other group within the schedule into a ramp segment.
When Multiple Ramp Schedules Per Transaction is turned on, you can’t add nonramped groups within ramp schedule groups.
You can’t create a group ramp schedule for groups that contain child groups.
You can’t create nested groups in group ramp segments.
You can’t apply renewal price uplifts tied to the Consumer Price Index (CPI) to ramped products.
You can’t create ramp deals for groups and ramp deals for lines in the same quote or order.
