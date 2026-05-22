---
article_id: ind.qocal_split_quote_to_orders_important_considerations.htm
title: Considerations for Creating Multiple Orders from a Quote
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_split_quote_to_orders_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Creating Multiple Orders from a Quote

Familiarize yourself with these limitations and functional behaviors that use the Advanced Order Creation From Quote feature to create multiple orders from a single quote. This information helps you determine when to use the API versus the user interface and how the system handles pricing and bundled products during the split process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Order Creation Limits and Requirements

Review these technical constraints and data handling rules before splitting quotes.

The Sales Transaction Line Editor experience excludes support for partial order creation, also known as ordering part of a quote.
The API alone supports the manual selection of specific line items that constitute a subset of a quote for a new order.
The Advanced Quote to Order API creates a partial order with a subset of lines and returns later to create more orders from that same quote.
Asset transfer source and destination quotes require the Create Single Order option.
The Transaction Management system prices and configures each created order independently.
New orders exclude cross-order pricing and tax calculations.
You can’t split bundled product components or line items that have pricing dependencies.
Splitting a quote with existing header level adjustments carries over the same pricing adjustments to the resulting orders created, but they aren’t re-applied to the orders. It’s best practice to not reprice orders when they’re created from a quote, so all pricing remains the same as the pricing from the original quote. Any further pricing operation causes those adjustments to be re-applied, which can result in over-discounted pricing.
You can’t split ramp groups.
Nested groups in quotes split into multiple orders.
A single quote supports a maximum split of 200 orders.
API Processing Behavior

The Create Orders From Quote API handles order headers and line items that use different processing methods.

ORDER TYPE	HEADER CREATION	LINE ITEM CREATION
Multiple Orders	Synchronous	Asynchronous
Single Order	Synchronous	Synchronous
