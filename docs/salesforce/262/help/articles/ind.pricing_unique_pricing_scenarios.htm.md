---
article_id: ind.pricing_unique_pricing_scenarios.htm
title: Unique Pricing Scenarios
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_unique_pricing_scenarios.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Unique Pricing Scenarios

Learn how complex pricing scenarios, from product interdependencies to honoring long-term customer agreements, impact sales efficiency and customer satisfaction. Discover how Salesforce Pricing provides the sophisticated capabilities needed to manage these unique challenges and drive revenue.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

When customers purchase a product, the price of dependent services or add-ons often changes based on the main item. This means sales reps must calculate prices manually, causing mistakes and slowing down sales. The inability to offer adaptive pricing options makes customers unhappy and costs organizations deals.

With Salesforce Pricing, you can track negotiated discounts and prices using contracts, derive one product's price from another, and distribute discounts programmatically.

Discount Distribution Service

Implement Derived Pricing
To accurately calculate a product’s price from another pricing source, such as a product or an asset, or the overall quote value, use the Derived Price feature.
Contract-Based Pricing
Manage and apply contact-based pricing deals on previously negotiated pricing agreements defined in a contract.
Establish Procedure Output Resolution
To select the definitive price for a product when pricing rules generate multiple outcomes, implement Procedure Output Resolution.
Apply Policy-Driven Price Revisions
Apply policy-driven price changes to respond to market conditions, contract terms, or inflationary trends. Pricing designers can define revision policies, track Consumer Price Index (CPI) data, and enable uplifts at set intervals, optimize revenue, and maintain business performance.
Promotion Execution Element
To apply promotions, add the Promotion Execution element to your pricing procedure. This element connects Global Promotions Management with Agentforce Revenue Management, executing applicable promotions for your transaction line items.
Pricing Action Parameters
To calculate the price of products directly from any object’s record page, use the Calculate Price button. All pricing actions are associated with a context definition and a pricing procedure so that the pricing data that is processed during the pricing process is stored directly in the Salesforce object.
Use Advanced Transaction Detail Line Pricing to Map Custom Fields
Users can update custom fields on sales transaction items or sales transaction item details through pricing procedures by using the Advanced Detail Line Pricing feature. With this feature, users no longer need to use custom triggers or flows to update those fields. This feature is useful for amendment, renewal, and cancellation use cases.
