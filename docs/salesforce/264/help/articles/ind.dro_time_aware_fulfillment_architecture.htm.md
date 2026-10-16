---
article_id: ind.dro_time_aware_fulfillment_architecture.htm
title: How Time-Awareness Works
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment_architecture.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# How Time-Awareness Works

Fulfillment Order Product and Fulfillment Asset records use the Fulfillment Asset State Period (FASP) object to track a subscription's state, quantity, and attributes over time. Each FASP record represents a fulfillment asset's distinct time segment, tied to an asset state period of the corresponding source asset. When a source asset has multiple asset state periods, Dynamic Revenue Orchestrator (DRO) creates multiple FASP records accordingly.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
When of a fulfillment asset's quantity or attributes change, DRO creates an FASP record to represent the new state. FASP records change the validity of an existing fulfillment asset or overwrite the fulfillment asset configuration for a specific time period.
When a state period is updated, DRO marks the previous FASP records as superseded. During order decomposition, it filters out superseded records and queries only the fulfillment asset's current state.
A nightly background job identifies assets with configuration end dates that passed and updates their current quantity and attributes to match the next effective state period.
