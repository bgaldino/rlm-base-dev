---
article_id: ind.dro_custom_scope_step_dependencies.htm
title: Apply Custom Scopes to Fulfillment Steps and Dependencies
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_custom_scope_step_dependencies.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-09-05
---

# Apply Custom Scopes to Fulfillment Steps and Dependencies

Use custom scopes to group fulfillment steps and resolve step dependencies based on a business value that you define, such as a tenant group, ramp segment, service location, or sales transaction item group. Standard scopes use a fixed level, such as Plan, Bundle, or Line Item.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
How a Custom Scopes Work

A fulfillment step scope controls the number of step instances Dynamic Revenue Orchestrator (DRO) creates. Use a custom scope on a fulfillment step definition to create one step instance for each distinct scope identifier.

A fulfillment step dependency scope controls which prerequisite step instances a dependent step waits for before it runs. Use a custom scope on a fulfillment step dependency definition to match dependent and prerequisite step instances that have the same scope identifier.

A step can use a standard scope when one of its dependencies uses a custom scope. If your step creation and dependency logic follow the same grouping, apply the same custom scope to the fulfillment step definition and dependency definition.

How a Custom Scopes Identifies a Business Group

DRO derives business groups by evaluating context tags mapped directly to these data fields.

The Sales Transaction Item tag maps to a scope value field on the order product.
The Fulfillment Transaction Item tag maps to a scope value field on the fulfillment order line item.

DRO evaluates these tags to read scope values for each item and groups items sharing the same value together. If DRO can't derive a scope identifier for an item, it assigns the Line Item scope by default.

See Create Custom Fulfillment Scope Configuration.

EXAMPLE

In this scenario, a custom scope named GroupScope uses the Sales Transaction Item Group as its context tag. An order contains four line items divided between two GroupScope values: two for Sales Cloud and two for Service Cloud.

Fulfillment Step Definitions

Fulfillment Step Definitions
FULFILLMENT STEP	FULFILLMENT STEP SCOPE	RESULT
Provision Tenant	Plan	DRO creates one plan-level step instance for the fulfillment plan.
Activate License	Line Item	DRO creates four step instances - one for each applicable order line item.
Notify Customer	Custom: GroupScope	DRO creates two step instances - one for each distinct GroupScope value.

Fulfillment Step Dependencies

Dependency Definitions
DEPENDENT STEP	PREREQUISITE STEP	DEPENDENCY SCOPE	RESULT
Activate License	Provision Tenant	Plan	Each line-item-level Activate License step waits for the plan-level Provision Tenant step.
Notify Customer	Activate License	Custom: GroupScope	Each custom-scoped Notify Customer step waits for Activate License steps whose source line items have the same GroupScope value.

Fulfillment Plan Created from the Custom Step and Dependency Scopes

Execution Logic
The Notify Customer step for Sales Cloud waits for the two Sales Cloud Activate License steps to complete.
The Notify Customer step for Service Cloud waits for the two Service Cloud Activate License steps to complete.
Steps in the other group don't delay either Notify Customer step.
