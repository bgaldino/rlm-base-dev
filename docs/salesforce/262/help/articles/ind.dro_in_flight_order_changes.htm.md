---
article_id: ind.dro_in_flight_order_changes.htm
title: In-Flight Order Changes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_in_flight_order_changes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# In-Flight Order Changes

Sometimes customers request modifications to their orders after the order is submitted for fulfillment by the sales rep. Modifications can include changing the entire order, specific line items, or even canceling part or all of the order. Changes that happen during fulfillment are called in-flight order changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Dynamic Revenue Orchestrator is enabled

Dynamic Revenue Orchestrator (DRO) accepts amended or canceled in-flight orders, decomposes the orders, reconciles changes, updates the orchestration plan, and runs the plan until fulfillment is complete.

Amending In-Flight Orders

Changes to an ongoing order, such as adjusting the provisioning date, adding order line items, and modifying certain attributes of the order line items, are referred to as in-flight order amendments.

Canceling In-Flight Orders

Reversing the purchasing decision or requesting to remove certain line items from the order is called canceling in-flight orders.

Point of No Return (PONR)

In the order fulfillment process, a critical stage is Point of No Return (PONR). This milestone marks the point in the fulfillment of a line item beyond which no amendments or cancellations can be made.

When sales reps change in-flight orders, the system identifies the line items that have reached PONR. Sales reps can then make informed decisions about how to proceed with honoring the customer's request.

Considerations for Changing In-Flight Orders
When you set up Dynamic Revenue Orchestrator (DRO) for in-flight order changes, it's important to understand exactly how DRO handles those changes.
Configure Inflight Plan Settings for a Fulfillment Step
As part of creating fulfillment steps, you can configure inflight plan settings to handle customer requests to add, amend, cancel, or otherwise change their order before the order is committed by a sales rep.
Point of No Return State Propagation
After an order item reaches Point of No Return (PONR), you can’t cancel or amend the order. When a PONR-marked fulfillment step transitions to an In Progress status, the PONR state change applies to the related commercial and technical products within the bundle, depending on the product type.
In-Flight Order Change Example
To help fulfillment designers understand how in-flight order changes work, refer to this example scenario.
