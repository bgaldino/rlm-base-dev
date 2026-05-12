---
article_id: ind.product_configurator_considerations_configuring_products_with_ramp_deals.htm
title: Considerations for Configuring Products with Ramp Deals
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_considerations_configuring_products_with_ramp_deals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Considerations for Configuring Products with Ramp Deals

When sales reps make configuration updates to products within a time-based ramp segment, the configurations in subsequent ramp segments are also impacted.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

Review these considerations before you configure products with line-level or group-level ramps.

For line-level ramps, configuration stays consistent across all ramp segments.
For group-level ramps, most configuration changes that you make in a ramp segment are applied to the current and subsequent segments. Previous segments remain unchanged to preserve data integrity.
Root or component quantity updates are segment-specific and don’t propagate to other segments.
If you include or exclude a child product within a bundle in one segment, that change also propagates to all subsequent segments. If you remove a child product from a segment while it continues to be included in previous segments, you can’t add it back again in subsequent segments. This is to avoid the creation of gaps in the ramp schedule.
Attribute changes made to a child product propagate only to the subsequent segments where that child product is already included.
Configuration rules override your manual ramp segment configurations, and are evaluated for each segment. 

For example, consider a configuration rule that states, "If T-shirt quantity is over 30, the color must be blue." Even if you manually set the color to red in a ramp segment where the T-shirt quantity is below 30, the configuration rule overrides this setting when the changes are propagated to subsequent segments. Any segment with T-shirt quantity of 31 or more automatically configures the color as blue.

Configuration rules don’t recognize quote or order groups. Consequently, when a rule adds a standalone product to a ramp segment—but not as part of a ramped product itself—it’s not automatically ramped or added to subsequent segments as expected. However, this behavior doesn’t affect child products of a ramped parent product. When a rule adds a child product to a parent that is already ramped, the child product is also ramped and added to subsequent segments.
You can’t ramp a parent bundled product if it contains a default One-Time or Evergreen child product with the Proportional quantity scaling method. A different scenario occurs if the child product isn't a default. While you can successfully ramp the parent bundle in this case, Configurator throws an error if you later try to enable the One-Time or Evergreen child product.
SEE ALSO
Set Up Ramp Deals for Groups in Revenue Cloud
Considerations for Creating Ramp Deals for Groups in Quotes and Orders
Considerations for Ramp Deals for Lines In Quotes and Orders
