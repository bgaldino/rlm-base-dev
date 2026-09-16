---
article_id: ind.pricing_stop_pricing.htm
title: Stop Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_stop_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Stop Pricing

Use the Stop Pricing element to stop the execution of the pricing procedure for a particular line item. This element acts as a conditional flow control mechanism. With it, you can create pricing logic where certain conditions trigger an early exit from the pricing procedure.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

When a line item reaches a Stop Pricing element:

The pricing procedure stops processing that line item immediately.
No subsequent pricing elements are executed for that line item.
The current pricing values are used as the final price.
During simulation, the Waterfall view shows where the pricing procedure stopped.
NOTE Stop Pricing only affects the specific line item that hits it. Other line items in the same transaction continue through the full pricing procedure normally.
When to Use Stop Pricing

Use the Stop Pricing element to implement exclusive pricing logic where certain conditions should prevent further pricing calculations.
