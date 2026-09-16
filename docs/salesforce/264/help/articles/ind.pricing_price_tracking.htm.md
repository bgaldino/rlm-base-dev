---
article_id: ind.pricing_price_tracking.htm
title: Track Price Ranges for Products
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_price_tracking.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Track Price Ranges for Products

Ensure transparent pricing policies and comply with regional directives by tracking a product's minimum and maximum prices over time using the Price Tracking element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

By tracking and showcasing a product's historical price fluctuations, like its lowest and highest price points over the last 30 days, customers gain a comprehensive understanding, empowering them to make informed purchasing decisions.

When you use the Price Tracking element, the fetched minimum and maximum prices are stored in the Product Price Range object. If a product's price frequently changes within a day, its daily price range is recorded in the Product Price History Log object. A product's price is determined by its combination with an associated price book, its product selling model, and the transaction currency.

Configure Price Tracking History
Track the minimum and maximum prices of a product over a period to help your users make well-informed buying decisions.
Update Your Product Price Range Entries Decision Table
For users who previously enabled minimum price tracking, update your decision table to include the newly introduced option for tracking maximum prices. If you enable maximum price in Price Tracking History settings without this update, your pricing procedure will fail during execution.
Price Tracking Actions
The price tracking element performs actions to help you fetch and record your product’s price range. Based on your business needs you can perform the required action using a pricing procedure.
