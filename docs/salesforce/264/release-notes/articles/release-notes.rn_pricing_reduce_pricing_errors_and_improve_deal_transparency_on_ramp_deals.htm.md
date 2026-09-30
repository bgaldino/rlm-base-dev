---
article_id: release-notes.rn_pricing_reduce_pricing_errors_and_improve_deal_transparency_on_ramp_deals.htm
title: Reduce Pricing Errors and Improve Deal Transparency on Ramp Deals
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_pricing_reduce_pricing_errors_and_improve_deal_transparency_on_ramp_deals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_pricing.htm
fetched_at: 2026-09-30
---

# Reduce Pricing Errors and Improve Deal Transparency on Ramp Deals

Calculate each segment's price uplift from the previous segment's uplift percentage instead of the original list price. Previously, uplifts on a ramp deal were always calculated from the product's original list price, so a 3-year deal with a $100 list price and a 10% annual uplift increased by $10 every year. Many multi-year agreements instead call for uplifts that compound: each year's increase applies to the prior year's already-uplifted price, not the original list price. Without compounding, sales teams calculated these prices manually outside the system, creating a risk of errors and reducing deal transparency for approvers.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

How: From the App Launcher, find and select Pricing Procedures. In your pricing procedure, on the Price Revision pricing element, select the compounding calculation method. To control uplift percentages by product, region, or term, use decision table rules together with the new UpliftCalculationMethod context tag.

SEE ALSO
Salesforce Help: Use the Price Revision Element in a Pricing Procedure
