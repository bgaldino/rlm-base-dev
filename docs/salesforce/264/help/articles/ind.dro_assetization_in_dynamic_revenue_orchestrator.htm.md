---
article_id: ind.dro_assetization_in_dynamic_revenue_orchestrator.htm
title: Fulfillment Assets
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_assetization_in_dynamic_revenue_orchestrator.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-11-23
---

# Fulfillment Assets

After an order is fulfilled, order line items and fulfillment order line items are converted to Salesforce assets.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Order line items are the items that customers order, such as phone or internet service. Fulfillment order line items are the products that order line items decompose into, such as a network interface controller. Upon fulfillment, order line items become Assets and fulfillment order line items become Fulfillment Assets.

Assets are created from order line items. View them on the Assets tab of the relevant Account page.
Fulfillment assets are created from fulfillment order line items. View them in the Fulfillment Asset section of the Related tab on the relevant Account page. If the Fulfillment Asset section doesn't appear, edit the layout for that page.

Commercial assetization creates or updates assets from order line items. Technical assetization creates or updates fulfillment assets from fulfillment order line items. At plan completion, Dynamic Revenue Orchestrator (DRO) starts commercial assetization and then technical assetization. If commercial assetization doesn't complete, see Retry Assetization for a Dynamic Revenue Orchestrator Order. For order line items that convert to assets at a staged assetize step instead of at plan completion, see Staged Assetize Step.

After assetization, the order's Orchestration Submission Status field shows one of these values.

ORCHESTRATION SUBMISSION STATUS	DESCRIPTION
Assetization Failed	Commercial or technical assetization didn't complete successfully.
Completed	The fulfillment plan, commercial assetization, and technical assetization completed successfully.

Dynamic Revenue Orchestrator reconciles fulfillment assets every 24 hours. It adjusts the quantity and validity of fulfillment assets based on the quantities of related assets and the asset state periods. If a technical product that is related to a fulfillment asset has fulfillment quantity calculation method set to Always one, the quantity field in the fulfillment asset is always one, regardless of the related asset quantities. If the calculation method is set to Aggregate, the quantity field in the fulfillment asset is the sum of the related asset quantities.

Fulfillment Asset Inactivation

When a fulfillment order line item's action is Cancel during order decomposition, DRO doesn't cancel the related fulfillment asset right away. Instead, DRO deactivates only the specific links between the fulfillment asset and the related assets whose order line items have the Cancel action. DRO deactivates a link when either of these conditions is true.

The related asset's asset state period is outside the current time.
The related asset's order line item action is Cancel, and DRO no longer uses that link to derive the fulfillment asset because a different decomposition rule now qualifies for that asset instead. In this case, DRO permanently deactivates the link, and it doesn't reactivate.

This reconciliation job also evaluates the fulfillment asset. It marks the fulfillment asset inactive only after all its links to related assets are inactive.

This inactivation behavior applies to ramped and non-ramped fulfillment assets that don't use time-awareness (time-agnostic fulfillment assets). For fulfillment assets that use time-awareness, see Order Decomposition With Time-Awareness.

SEE ALSO
Retry Assetization for a Dynamic Revenue Orchestrator Order

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_assetization_in_dynamic_revenue_orchestrator.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
