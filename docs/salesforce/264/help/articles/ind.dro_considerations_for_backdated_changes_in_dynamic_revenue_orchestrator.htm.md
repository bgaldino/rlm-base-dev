---
article_id: ind.dro_considerations_for_backdated_changes_in_dynamic_revenue_orchestrator.htm
title: Considerations for Backdated Changes in Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_considerations_for_backdated_changes_in_dynamic_revenue_orchestrator.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# Considerations for Backdated Changes in Dynamic Revenue Orchestrator

Review how Dynamic Revenue Orchestrator (DRO) decomposes and orchestrates backdated amend, renew, and cancel orders and rolls back amend and renew orders. Understand the behavior and constraints when time-awareness isn't turned on.

Backdated Amend, Renew, and Cancel Orders

A backdated order captures a change to an asset that's effective from a past date. When you submit a backdated amend, renew, or cancel order to DRO, DRO updates the Fulfillment Asset (FA) and orchestrates the change. Review these behaviors.

Decomposition and plan composition for a backdated order are the same as for an order that's effective today. DRO decomposes the order line items, determines the action for each Fulfillment Order Line Item (FOLI), and composes an orchestration plan.
Orchestration steps run no sooner than today. A step that's based on a past effective date runs as soon as it's in progress, and DRO doesn't flag the step as in jeopardy.
For a backdated cancel order, a line item-scoped FA is canceled on the effective date. An account-scoped FA is canceled on the effective date only when no related asset is active on that date.
For a backdated renewal order, DRO reactivates an FA whose related asset expired. To reactivate an expired asset, submit a renewal order that extends the asset's term.

To submit a backdated amend, renew, or cancel order, see Backdate Asset Transactions. For the requirements and limitations that apply to backdated changes, see Considerations for Assets with Backdated Changes.

Behavior When Time-Awareness Isn't Turned On

With time-awareness, DRO evaluates the past, current, and future state of an FA when it determines fulfillment actions. When time-awareness isn't turned on, FAs are time-agnostic and DRO determines fulfillment actions from the current state of the FA only.

Without time-awareness, a backdated or future-dated change can result in an incorrect action for a fulfillment line. For example, DRO can determine an Add action instead of an Amend action, or a No Change action instead of a Cancel action.
To decompose and orchestrate backdated amend, renew, and cancel orders correctly, turn on time-awareness. See Turn On Time-Awareness.
Rollback Orders

You can roll back a backdated or future-dated amendment or renewal. When you submit a rollback order, DRO reverses the change and returns the asset and its related Fulfillment Assets to the state they had before the transaction.

You can roll back an amendment or renewal order, whether it's backdated or future-dated.
You can't roll back a cancellation.
You can't roll back an initial sale, a transfer, or a rollback.
You can't roll back an amendment or renewal that added or removed a product in a bundle.

For the full list of rollback requirements and limitations, see Transaction Rollbacks Considerations.

Swap Orders

DRO decomposes and fulfills swap orders that upgrade or downgrade an asset to a different product. DRO doesn't evaluate constraint rules on swap orders, so swap eligibility that's governed by constraint rules isn't enforced during orchestration.
