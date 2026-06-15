---
article_id: ind.qocal_ramp_deals.htm
title: Divide Subscription Transactions into Segments with Ramp Deals for Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Divide Subscription Transactions into Segments with Ramp Deals for Lines

With ramp deals for lines in quotes and orders, show a subscription-based product as a single transaction line such as a quote line item divided into segments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled

Each segment can vary in price, quantity, and discount over different time periods. Your sales reps can use ramp deals to capture their customer’s evolving needs over time within a single transaction. With greater flexibility in the pricing strategy, they can maintain long-term relationships with their customers, and help your business grow with predictable profits.

You can create ramp segments over the transaction line’s subscription term and segment type. The subscription term defines the duration of the transaction line and the segment type is applied on the subscription term. The segment type for a ramp deal is Yearly, Custom, or Trial.

For example, let’s consider a transaction line with a subscription term of 36 months, an Annual segment type, and a free trial of 30 days. This setup generates four segments: one for each year and one for the trial. Each segment can have its own quantity and discount.

Segments created for a transaction line appear on the transaction line's related list. To view or modify these segments, open the Ramp Deal window from the transaction line. After you save the segments, the total price of the transaction line is shown on the Line Item Details tab. If Instant Pricing is off, you can view the updated prices in the Transaction Line Editor component.

Considerations for Ramp Deals for Lines In Quotes and Orders
Correct configuration of ramp deals is crucial to make sure they function as intended in Transaction Management. Review the considerations before you create or update ramp deals.
Configure Ramp Segments in Ramp Deals for Lines
Divide a transaction line such as a quote line item or an order product into multiple ramp segments, each with its own unique price and quantity over different time periods.
