---
article_id: ind.qocal_create_ramp_deal_for_groups_for_usage_products.htm
title: Ramp Deals for Usage Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_ramp_deal_for_groups_for_usage_products.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_complex_long_term_multiple_products.htm
fetched_at: 2026-09-04
---

# Ramp Deals for Usage Products

Use ramp deals for groups for usage products to break down a long-term deal into smaller time-based segments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.

Look at DataFlow, a software company that sells a data transfer service with tiered pricing based on usage. They want to offer a promotional deal to a new customer, GlobalCorp, for a three-year contract.

Set Up Subscription: GlobalCorp signs a three-year subscription. The sales rep sets up a ramp deal with three annual group segments.
Group Products: The rep creates a Data Transfer Services group containing usage products like inbound and outbound data transfer.
Define Ramp Schedule: The rep defines the ramp schedule for the group, with each segment lasting one year.
Ramp 1 (Year 1): To attract GlobalCorp, DataFlow offers a 20% discount on all data transfer usage for the first year.
Ramp 2 (Year 2): The discount is reduced to 10% for the second year.
Ramp 3 (Year 3): Rating is done on the standard rate, and DataFlow includes a loyalty grant of 100 GB of data transfer at no additional cost, to encourage renewal.
Billing: As GlobalCorp uses the service, usage management automatically applies the correct pricing for each year.

When you add a usage product to a ramp deal, the initial addition copies rates to all segments. After that, manage usage of products in ramp segments as follows.

ACTION	DESCRIPTION	CONSIDERATIONS
Rate Changes	Modify the rate of a usage product within a segment.	The initial product addition copies rates to all segments. However, subsequent modifications to a rate in a segment apply only to that specific segment—rate changes don't carry to other segments.
Binding Type Changes	Change the binding type per segment.	Changes to the binding type propagate across all segments with the same ramp identifier, because binding types are consistent for the entire deal. This propagation happens both forward and backward through the segments.
Grant Changes	Modify the grant quantity for a usage product within a segment.	The grant quantity can be changed on a per-segment basis.
