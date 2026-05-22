---
article_id: ind.pricing_subscription_pricing_proration.htm
title: Manage Pricing Using Proration and Subscription Elements
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_subscription_pricing_proration.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Manage Pricing Using Proration and Subscription Elements

Use the Proration and Subscription elements in Salesforce Pricing to apply time-based pricing when a customer starts, cancels, or changes a subscription mid-cycle. These elements ensure customers are charged only for the time they ‌use your product or service.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled

The Subscription element calculates the total subscription price based on the input unit price and the pricing term count. When a subscription starts, changes, or ends mid-period, the Proration element calculates a multiplier based on the portion of the period used. This multiplier then adjusts the subscription price, ensuring customers are only priced based on their subscription time.

For example, if a customer starts a subscription to a software service in the middle of a pricing period, they are charged only for the time they ‌use it. If the pricing period is monthly and the customer begins their subscription on the 15th of the month, they are charged only for the remaining 15 days. The full monthly charge is then applied on the first day of the next month.

Configure Proration Settings
Set custom pricing term values to calculate product prices based on your customer's subscription length.
Learn About the Proration Multiplier
The proration multiplier is used to adjust the price of a product or service based on a customer’s usage. This multiplier can be calculated when a customer subscribes to a service partway through a pricing period or when there are changes to the service, such as upgrades, downgrades, or cancellations. The multiplier calculation is based on how long the customer uses the service during the pricing period.
Common Proration Examples
These examples demonstrate how various proration settings impact the final subscription price for a product with a Selling Model Type of TermDefined.
Configure the Proration and Subscription Element
To calculate time-based pricing, use the Proration and Subscription elements.
