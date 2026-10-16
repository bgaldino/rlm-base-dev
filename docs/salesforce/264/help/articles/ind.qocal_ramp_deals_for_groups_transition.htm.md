---
article_id: ind.qocal_ramp_deals_for_groups_transition.htm
title: Ramp Deals for Lines vs. Ramp Deals for Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals_for_groups_transition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.understanding_ramp_deals.htm
fetched_at: 2026-09-04
---

# Ramp Deals for Lines vs. Ramp Deals for Groups

There are two types of ramp deals in Revenue Management - Ramp Deals for Lines and Ramp Deals for Groups.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
Ramp Deals for Groups

Apply ramp segments at the group level, covering all eligible products within a group together. This is the recommended approach for new implementations. All subscription products that meet the requirements are eligible by default — no per-product configuration in Product Catalog Management is needed. To provide trials at no additional cost with ramp deals for groups, sales reps apply a 100% manual discount to segments at the group or line level.

Ramp deals for groups offer several advantages over ramp deals for lines:

Supports bundle products. Configuration changes made to a ramp segment automatically propagate to that segment and all subsequent segments.
Supports usage products. You can specify different rates across ramp segments.
Supports unit price uplifts per segment for precise, transparent pricing.
Shows segments in quote documents, making it easier to collaborate with customers.
Supports amending ramped assets to adjust prices and change field values.
Supports trial and pro-rated segments.
Available on Experience Cloud sites.

If you're currently using ramp deals for lines, Salesforce recommends transitioning to ramp deals for groups. You can run both approaches in parallel during migration, but you can't mix them in the same quote or order.

Ramp Deals for Lines

Apply ramp segments at the individual transaction line level. A subscription-based product appears as a single quote line item divided into segments, each with its own price, quantity, and discount. To use this approach, admins configure product ramp segments in Product Catalog Management — only products explicitly set up with ramp segments are eligible. To provide trials at no additional cost with ramp deals for lines, you create product segments with the Free Trial segment type.

IMPORTANT Salesforce recommends that you use Ramp Deals for Groups only.
