---
article_id: ind.product_configurator_considerations_configuring_products_with_ramp_deals.htm
title: Add Products to a Ramp Deal
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_considerations_configuring_products_with_ramp_deals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.qocal_ramp_deals_complex_long_term_multiple_products.htm
fetched_at: 2026-09-04
---

# Add Products to a Ramp Deal

After creating the ramp structure, add products to segments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
To manage ramp deals for quote line item groups:	Create on Quotes
To manage ramp deals for order product groups:	Create on Orders
IMPORTANT Before you begin, complete steps 5 to 7 in Prerequisites: Ramp Deals for Groups to select a catalog and then add products from the catalog to their associated record pages.
Click Show more actions on the segment, then click Browse Catalogs.
Select a catalog, and then click Next.
Add products, and then click Next.
Select the group ramp segments to add products to:
Current Segment Only: Adds products as non-ramped lines.
Current and Subsequent Segments: Adds rampable products as ramped lines and other products as non-ramped lines.
NOTE You see the options to select segments only after your admin configures the Discover Products flow.

After adding products, update quantities, discounts, and configurations on each line. Configuration changes propagate to subsequent segments automatically.
