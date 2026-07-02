---
article_id: ind.dro_assetization_in_dynamic_revenue_orchestrator.htm
title: Fulfillment Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_assetization_in_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Fulfillment Assets

After an order is fulfilled, order line items and fulfillment order line items are converted to Salesforce assets.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Order line items are the items that customers order, such as phone or internet service. Fulfillment order line items are the products that order line items decompose into, such as a SIM card or a network interface controller. Upon fulfillment, both order line items and fulfillment order line items become assets.

Assets are created from order line items. View them on the Assets tab of the relevant Account page.
Fulfillment assets are created from fulfillment order line items. View them in the Fulfillment Asset section of the Related tab on the relevant Account page. If the Fulfillment Asset section doesn't appear, edit the layout for that page.

Dynamic Revenue Orchestrator reconciles fulfillment assets every 24 hours. It adjusts the quantity and validity of fulfillment assets based on the quantities of related assets and the asset state periods. If a technical product that is related to a fulfillment asset has fulfillment quantity calculation method set to Always one, the quantity field in the fulfillment asset is always one, regardless of the related asset quantities. If the calculation method is set to Aggregate, the quantity field in the fulfillment asset is the sum of the related asset quantities.
