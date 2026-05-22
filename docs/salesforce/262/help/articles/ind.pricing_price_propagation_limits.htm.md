---
article_id: ind.pricing_price_propagation_limits.htm
title: Price Propagation Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_price_propagation_limits.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Price Propagation Limits

Before adding the Price Propagation element to your pricing procedure, keep these points in mind:

You can add only one Price Propagation element per pricing procedure.
The Price Propagation element is not compatible with Derived Pricing, Map Line Item, and Promotions elements. Do not include these elements in the same pricing procedure.
The Price Propagation element is not supported inside a list group.
If delta pricing is enabled, copy the net unit price value before the propagation element runs and save it in a separate tag. Use the tag in your propagation table and formulas.
Do not use the propagation element in pricing procedures for amend, renew, or cancel transactions. Doing so may result in inaccurate pricing.
Do not use the propagation element as a substitute for formula or aggregate elements. It is designed for specific roll-up logic and behaves differently than standard calculation elements.
Deselecting Enable Propagation doesn't delete the propagation configuration. The settings remain in the Pricing Setting JSON to prevent data loss if you re-enable the feature. To reset the configuration, remove the Pricing Setting element and add it again.
