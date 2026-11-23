---
article_id: ind.dro_fulfillment_order_line_item_actions.htm
title: Fulfillment Order Line Item Actions
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_order_line_item_actions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-11-23
---

# Fulfillment Order Line Item Actions

When an order is decomposed, each fulfillment order line item gets an action that's derived from the related order line item actions.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
Fulfillment Order Line Item Actions

When Dynamic Revenue Orchestrator (DRO) decomposes asset-based orders, it compares the attributes and quantity of the order line items with the attributes and quantity of the related fulfillment asset.

DRO determines and sets the actions on the decomposed fulfillment order line items based on the changes in the attributes and quantity of the order line items.

This table shows how DRO determines fulfillment order line item actions for fulfillment assets that don't use time-awareness (time-agnostic fulfillment assets). For fulfillment assets that use time-awareness, see How Dynamic Revenue Orchestrator Determines Actions for Time-Aware Assets.

ORDER LINE ITEM ACTION	FULFILLMENT ORDER LINE ITEM ACTION	DESCRIPTION
Add	Add	DRO sets the value and creates a fulfillment asset after the fulfillment plan is completed.
Amend	Amend	

DRO sets the value when the attribute values or quantity of the order line items related to the decomposed fulfillment order line item change.

After the plan is complete, DRO updates the fulfillment asset that's related to the fulfillment order line item.


No Change	No Change	DRO sets the value when the attribute values or quantity of the order line items that are related to the decomposed fulfillment order line item don’t change. There's no change to the fulfillment asset.
Renew	Renew	DRO sets the value when the order line item is submitted to renew the lifecycle of a product.
Cancel	Cancel	DRO sets the value only when all order line items related to the fulfillment order line item have the Cancel action, even if other uncanceled assets also share the fulfillment asset.
NOTE

When a fulfillment order line item's action is Cancel, DRO doesn't cancel the fulfillment asset. It deactivates only the specific links to the canceled order line items. See Fulfillment Assets for how DRO deactivates links and when it marks the fulfillment asset inactive.

NOTE

During order decomposition, if the enriched fulfillment order line item contains different attribute values and quantity than its fulfillment asset, then DRO sets the fulfillment order line item's action as Amend, irrespective of the action on its related order line item.

Understand order line items. See Order Line Item Actions.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_order_line_item_actions.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
