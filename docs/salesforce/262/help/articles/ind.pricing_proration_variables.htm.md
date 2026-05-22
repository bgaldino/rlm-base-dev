---
article_id: ind.pricing_proration_variables.htm
title: Learn About the Proration Multiplier
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_proration_variables.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Learn About the Proration Multiplier

The proration multiplier is used to adjust the price of a product or service based on a customer’s usage. This multiplier can be calculated when a customer subscribes to a service partway through a pricing period or when there are changes to the service, such as upgrades, downgrades, or cancellations. The multiplier calculation is based on how long the customer uses the service during the pricing period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
TIP Salesforce Pricing supports month-plus-day ‌proration types for any frequency term.

Here's how Salesforce Pricing calculates prorated subscription costs.

SUBSCRIPTION PRORATE PRECISION	CALCULATE THE PRORATE MULTIPLIER	EXAMPLE
Month	Calculate the duration of the subscription term in full months and divide it by the product’s subscription term. If the duration includes a partial month, Salesforce Pricing adjusts the total number of months to the nearest whole number.	

A service costs $50 per month. If a customer subscribes on the 15th of the month and the month ends on the 30th, the customer only uses the service for half the month (15 days out of 30).

To calculate the proration multiplier, use this formula - Proration Multiplier = Time Used/ Total Time in Period

In this case: 15 days/ 30 days = 0.5

To calculate the adjusted price: $50 X 0.5 = $25.
