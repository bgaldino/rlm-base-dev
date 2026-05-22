---
article_id: ind.dro_design_time_orchestration.htm
title: Design Your Order Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_design_time_orchestration.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Design Your Order Orchestration

Build strategic, efficient, and adaptable order orchestration in Dynamic Revenue Orchestrator (DRO). Create order fulfillment steps, fulfillment step groups, dependencies, and rules for how DRO fulfills orders. Fulfillment steps can be automated, manual, or dependent on other steps.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Order Orchestration runs after decomposition completes. If you haven't designed your decomposition rules yet, see Design Your Order Decomposition.

You can decide the depth at which to implement orchestration in DRO. Orchestration can a simple fulfillment tracker, with most of the fulfillment details handled by your ERP, or use DRO to more deeply model your orchestration.

To get started designing your order orchestration solution, follow these instructions:

/apex/HTViewHelpDoc?id=ind.Chunk812670325.htm#dro_define_orchestration_components

/apex/HTViewHelpDoc?id=ind.Chunk99891604.htm#fulfillment_step_types

In-Flight Order Changes
Sometimes customers request modifications to their orders after the order is submitted for fulfillment by the sales rep. Modifications can include changing the entire order, specific line items, or even canceling part or all of the order. Changes that happen during fulfillment are called in-flight order changes.
Import a Fulfillment Step Definition Group
To help scale your fulfillment plans, and ensure consistency across plans, you can import your existing fulfillment step definition groups directly from a fulfillment workspace.
Set Dependencies Between Fulfillment Steps
Connect fulfillment step definitions to create a dependency between them. When an order is submitted, the steps run in the order that you define.
/apex/HTViewHelpDoc?id=ind.Chunk77831582.htm#dro_create_a_fulfillment_task_assignment_rule

/apex/HTViewHelpDoc?id=ind.Chunk2074307057.htm#dro_configure_scenarios_for_a_fulfillment_step_definition_group

/apex/HTViewHelpDoc?id=ind.Chunk1561723041.htm#dro_define_conditions_for_a_fulfillment_step_to_run

/apex/HTViewHelpDoc?id=ind.Chunk592923844.htm#dro_configure_steps_for_future_execution
