---
article_id: ind.dro_ramp_deal_decomposition.htm
title: Decompose Ramp Deal Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_ramp_deal_decomposition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Decompose Ramp Deal Orders

Use Dynamic Revenue Orchestrator to decompose and fulfill ramp deals. A ramp deal is an order containing standalone line items that are divided into segments. Each segment can vary in price, quantity, and discount over different periods.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
NOTE If you aren't familiar with how ramp deals work, see Divide Subscription Transactions into Segments with Ramp Deals for Lines.
Assetize Ramp Deal Orders

Dynamic Revenue Orchestrator (DRO) assetizes fulfillment order line items and fulfills the orders according to the subscription, term, and quantity defined in the corresponding segment. The decomposition scope determines how fulfillment order line items are assetized:

Order Line Item scope: A single fulfillment asset is created for each fulfillment order line item.
Account scope: A single fulfillment asset is created for each account.
Order scope: Fulfillment assets aren’t created.

For example, let’s consider an order line item with a subscription term of 36 months, an Annual segment type, and a free trial of 30 days. This setup generates four segments: one for each year and one for the trial period. Each segment can have its own quantity and pricing.

DRO automatically applies the quantity and pricing at the start of each year, immediately following the free trial period, as specified in the four segments.

Ramp Order Considerations

Here are some points to remember when you decompose ramp deal orders:

You must enable the rampDealForQocal setting in your org and make sure that the order line items have the ramp and segment identifiers populated.
If time-awareness isn't turned on, for Amend, Renew, and Cancel orders, the same order action is applied to individual segments even if there's no change to a segment. Additionally, DRO calculates the action on the fulfillment order lines based on the order action applied to the order line items. If you amend, renew, or cancel an order, the action affects every segment of that order, and DRO processes the fulfillment accordingly.
If time-awareness isn't turned on and the fulfillment plan for a ramp order includes a Staged Assetize step associated with the ramp segments, then the Staged Assetize step is skipped, and all the segments are assetized when the fulfillment plan is completed. See Fulfillment Step Types.
