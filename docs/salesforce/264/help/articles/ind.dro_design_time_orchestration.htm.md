---
article_id: ind.dro_design_time_orchestration.htm
title: Design Your Order Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_design_time_orchestration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator.htm
fetched_at: 2026-09-05
---

# Design Your Order Orchestration

Build strategic, efficient, and adaptable order orchestration in Dynamic Revenue Orchestrator (DRO). Create order fulfillment steps, fulfillment step groups, dependencies, and rules for how DRO fulfills orders. Fulfillment steps can be automated, manual, or dependent on other steps.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Order Orchestration runs after decomposition completes. If you haven't designed your decomposition rules yet, see Design Your Order Decomposition.

You can decide the depth at which to implement orchestration in DRO. Orchestration can a simple fulfillment tracker, with most of the fulfillment details handled by your ERP, or use DRO to more deeply model your orchestration.

To get started designing your order orchestration solution, follow these instructions:

Define Orchestration Plan Components
Create and organize fulfillment steps, their dependencies, and fulfillment processes in fulfillment workspaces.
Fulfillment Step Types
When you plan your orchestration, keep in mind the different types of fulfillment steps, and how they work. Fulfillment step types can be used to define manual tasks, automated tasks, milestones, callouts, and other actions.
Design Orchestration with the High Tech Order Orchestration Template
Use the High Tech Order Orchestration Template as a starting point for orders that combine project work, hardware assembly, software provisioning, billing, and revenue scheduling.
In-Flight Order Changes
Sometimes customers request modifications to their orders after the order is submitted for fulfillment by the sales rep. Modifications can include changing the entire order, specific line items, or even canceling part or all of the order. Changes that happen during fulfillment are called in-flight order changes.
Import a Fulfillment Step Definition Group
To help scale your fulfillment plans, and ensure consistency across plans, you can import your existing fulfillment step definition groups directly from a fulfillment workspace.
Set Dependencies Between Fulfillment Steps
Connect fulfillment step definitions to create a dependency between them. When an order is submitted, the steps run in the order that you define.
Create a Fulfillment Task Assignment Rule
Create reusable rules to automatically assign manual tasks to users based on the criteria and conditions defined in the rule.
Configure a Fulfillment Scenario
Use a fulfillment scenario to define when Dynamic Revenue Orchestrator (DRO) adds a fulfillment step definition group to a fulfillment plan after an order is submitted. Fulfillment scenarios help you add common fulfillment steps automatically instead of creating the steps for each order.
Define Conditions for a Fulfillment Step to Run
You can prevent a fulfillment step from running until certain conditions are met.
Configure Steps for Future Execution
Fulfillment designers can configure the steps to be executed at a future date and time. They can set a delay for the execution of steps based on the start date of the source line item, the execution time of the previous steps, or a custom date based on a context definition field.
Apply Custom Scopes to Fulfillment Steps and Dependencies
Use custom scopes to group fulfillment steps and resolve step dependencies based on a business value that you define, such as a tenant group, ramp segment, service location, or sales transaction item group. Standard scopes use a fixed level, such as Plan, Bundle, or Line Item.
