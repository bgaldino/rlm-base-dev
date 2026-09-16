---
article_id: ind.dro_time_aware_plan_sequence.htm
title: Orchestrate Orders with Time-Awareness
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_time_aware_plan_sequence.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_time_aware_fulfillment.htm
fetched_at: 2026-09-05
---

# Orchestrate Orders with Time-Awareness

Dynamic Revenue Orchestrator (DRO) sequences fulfillment steps across time period. Steps for a future period wait for the preceding period to finish, while configured dependencies continue to control the order of execution within each period.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

When DRO creates an orchestration plan for a time-aware order, it groups instantiated fulfillment steps that apply to the same time period. DRO sequences these groups according to the start and end dates and times of the steps’ sources. It then adds dependencies from the applicable final steps in one group to the applicable first steps in the next group. As a result, fulfillment for a later period begins only after the required fulfillment for the preceding period finishes.

DRO preserves dependencies configured within each time period, including dependencies that use Plan, Bundle, Line Item, or Custom scope. Steps in the same period can run in parallel unless a configured dependency requires them to run sequentially. If a group has multiple first or final steps, DRO connects the applicable steps so that the required steps in the preceding period finish before the dependent steps in the next period begin.

NOTE
To sequence fulfillment correctly across time periods, configure the required dependencies and scopes in the fulfillment step definitions and step dependencies. DRO preserves this configuration within each time period and uses it when connecting one time-period group to the next.
A fulfillment step whose sources span multiple time periods can remain shared across the periods instead of belonging to a single time-period group.
Example: Fulfillment Across Time Periods

Consider an order with a two-year ramp for Sales Cloud and Service Cloud. In year 1, the plan runs Provision Tenant, Activate License, and Notify Customer according to their configured dependencies and scopes. Steps without dependencies between them run in parallel. DRO sequences the groups of instantiated steps according to the start and end dates and times of their sources. The applicable year 2 steps start only after the required Year 1 steps finish.
