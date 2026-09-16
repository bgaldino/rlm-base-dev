---
article_id: ind.pricing_view_setup_objects_price_waterfall.htm
title: Understand the Setup Objects Used for Price Waterfall
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_view_setup_objects_price_waterfall.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_set_up_price_waterfall_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Understand the Setup Objects Used for Price Waterfall

Price Waterfall uses setup objects to capture logs for how a pricing procedure ran, making it easy for your users to explain and check pricing calculations at each step. For example, pricing analysts can check the number of discounts applied at various tiers while calculating volume discounts.

Salesforce Pricing has predefined Price Waterfall objects.

Pricing Waterfall Subtype Definition
Defines the types of applications by using the Price Waterfall component.
Pricing Waterfall Business Process Type Definition
Defines the types of business processes that are applied to the pricing procedure.
Pricing Waterfall Explainability Action Definition
Defines where the metadata of your pricing procedure is stored.
Pricing Waterfall Explainability Action Version
Defines and stores versions of the explainability actions used by pricing procedures.

To view the pricing waterfall setup objects, from Setup, in the Quick Find box, search and select Decision Explainer. The Price Waterfall setup objects are visible with the associated Decision Explainer objects.
