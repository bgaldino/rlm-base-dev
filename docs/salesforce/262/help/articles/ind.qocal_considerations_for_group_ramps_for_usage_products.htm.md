---
article_id: ind.qocal_considerations_for_group_ramps_for_usage_products.htm
title: Considerations for Managing Ramp Deals for Groups for Usage Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_for_group_ramps_for_usage_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Managing Ramp Deals for Groups for Usage Products

Learn how to effectively manage your ramp segments for usage products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
ACTION	DESCRIPTION	CONSIDERATIONS
Rate Changes	Modify the rate of a usage product within a segment.	The initial product addition copies rates to all segments. However, subsequent modifications to a rate in a segment applies only to that specific segment; rate changes don't carry to other segments.
Binding Type Changes	Change the binding type per segment.	Changes to the binding type propagate across all segments with the same ramp identifier, because binding types are consistent for the entire deal. This propagation happens both forward and backward through the segments.
Grant Changes	Modify the grant quantity for a usage product within a segment.	The grant quantity can be changed on a per-segment basis.
