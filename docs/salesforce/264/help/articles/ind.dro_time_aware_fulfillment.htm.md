---
article_id: ind.dro_time_aware_fulfillment.htm
title: Order Fulfillment With Time-Awareness
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_fulfillment.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_run_time_administration.htm
fetched_at: 2026-09-05
---

# Order Fulfillment With Time-Awareness

Manage complex, multi-year subscription lifecycles by using time-awareness in fulfillment assets. Instead of using a static snapshot of an asset, time-awareness aligns orchestration with the effective dates of each change, so that additions, cancellations, and renewals of backdated and future-dated orders update only the assets that change in that period.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Time-awareness is ideal for multi-year deals in which product configurations, such as quantity and attributes, change over time. It's especially useful for managing ramp deals, where annual changes occur within a single multi-year contract.

For example, a customer signs a 3-year subscription for 100, 200, and 300 licenses in Years 1, 2, and 3. If they amend Year 1 to add 50 licenses, time-aware fulfillment updates only Year 1 and leaves Years 2 and 3 unchanged.

How Time-Awareness Works
Fulfillment Order Product and Fulfillment Asset records use the Fulfillment Asset State Period (FASP) object to track a subscription's state, quantity, and attributes over time. Each FASP record represents a fulfillment asset's distinct time segment, tied to an asset state period of the corresponding source asset. When a source asset has multiple asset state periods, Dynamic Revenue Orchestrator (DRO) creates multiple FASP records accordingly.
Orchestrate Orders with Time-Awareness
Dynamic Revenue Orchestrator (DRO) sequences fulfillment steps across time period. Steps for a future period wait for the preceding period to finish, while configured dependencies continue to control the order of execution within each period.
How Dynamic Revenue Orchestrator Determines Actions for Time-Aware Assets
When you turn on time-awareness, Dynamic Revenue Orchestrator (DRO) evaluates the state of a Fulfillment Asset (FA) record and its Fulfillment Asset State Period (FASP) records before and after technical assetization, along with any attribute changes. DRO then determines the decomposition action for a given period.
Migrate Fulfillment Assets from Time-Agnostic to Time-Aware
Attribute values of Fulfillment Asset (FA) records created before time-awareness reflect only the most recent assetization state and not the values that were in effect during each asset state period in the past. When you submit an Amend, Renew, or Cancel order on these assets, decomposition can derive the wrong fulfillment order line item action for the affected period. Also, the resulting fulfillment asset state period (FASP) values can be incorrect.
Example: Add Action with Time-Awareness Turned On
Let's see how Dynamic Revenue Orchestrator (DRO) uses time-awareness to decompose a multi-year ramp deal into fulfillment order line items (FOLIs) and Fulfillment Asset State Period (FASP) records that align with each year's effective dates.
Example: Mid-Year Amendment with Split Fulfillment Asset State Periods
Let's see how Dynamic Revenue Orchestrator (DRO) uses time-awareness to split existing Fulfillment Asset State Period (FASP) records when a new contract starts mid-year, and how it derives No Change, Amend, and Renew actions for the overlapping timeline.
Considerations for Backdated Changes in Dynamic Revenue Orchestrator
Review how Dynamic Revenue Orchestrator (DRO) decomposes and orchestrates backdated amend, renew, and cancel orders and rolls back amend and renew orders. Understand the behavior and constraints when time-awareness isn't turned on.
SEE ALSO
Turn On Time-Awareness
