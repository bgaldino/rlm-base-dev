---
article_id: ind.dro_set_dependencies_between_fulfillment_steps.htm
title: Set Dependencies Between Fulfillment Steps
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_set_dependencies_between_fulfillment_steps.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-09-05
---

# Set Dependencies Between Fulfillment Steps

Connect fulfillment step definitions to create a dependency between them. When an order is submitted, the steps run in the order that you define.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To set dependencies between fulfillment steps:	

Fulfillment Administrator

OR

Fulfillment Designer

IMPORTANT If you set up dependencies that result in a loop, the entire fulfillment process is at risk of failing. For example, if you make Step A dependent on Step B, and then make Step B dependent on Step A, you have a loop.

The Fulfillment Workspace arranges the step definitions in the order that they're completed when an order is submitted.

To create a dependency between steps, follow these instructions.

From the App Launcher, find and select Fulfillment Workspaces.
On the step definition that must finish first, click .
On the step definition that must finish last, click .
Select the Dependency Scope.
For steps in the same plan that follow a standard hierarchy, match the dependency scope to the scope of the depends-on step.
For steps in different plans, select Cross Plan.
For steps that are grouped by a business value, select Custom. Then, in Custom Scope, select an existing custom fulfillment scope.
To learn how custom scopes affect step instances and their dependency relationships, see How Custom Scopes Apply to Fulfillment Steps and Dependencies.
NOTE Cross Plan Scope Considerations:
For the Cross Plan scope, one instance of the step appears per plan when a step in one plan is dependent on a step that’s in another plan.
To use the Cross Plan scope, make sure to configure the Cross Plan context definition in Sales Transaction Context Definition. Then add or import the fulfillment step groups within the Fulfillment Workspace. See Create Custom Context Definitions for Order Orchestration.
NOTE Propagate State to Dependent Step Considerations:
Use the Propagate State to Dependent Step option only if you have created a dependency between a call out or auto task step and a pause step.
After defining the dependency and propagating the state to the dependent step, you can’t change the step type value, unless you first set the Propagate State to Dependent Step value to None.
NOTE In-flight Change Considerations:
When a step is amended or canceled because of an in-flight change in the plan, configure whether the step state must propagate to the following step by using the Propagate State to Dependent Step field. The options are - None, Amended, Canceled, and Both.
When a step is canceled because of an in-flight change in the plan, to reverse the order of step group execution, select the Execute Cancel Step Groups In Reverse Order checkbox.
EXAMPLE

A step's scope determines how many instances of that step DRO creates when an order is fulfilled.

Plan: DRO creates one instance of the step for the entire order.
Bundle: DRO creates one instance of the step for each bundle in the order.
Line Item: DRO creates one instance of the step for each order line item.

For all the scope values, see Define a Fulfillment Step.

In a dependency, Step A depends on Step B, so Step B must finish before Step A can start. The dependency scope determines which Step B instance each Step A waits for. To create common dependency patterns, set the step scopes and the dependency scope as shown in this table.

Scope Settings for Common Dependency Patterns
TO CREATE	SET STEP B SCOPE TO	SET STEP A SCOPE TO	SET DEPENDENCY SCOPE TO
Multiple Step B and one Step A	Line Item	Plan	Line Item
One Step B and multiple Step A	Plan	Line Item	Plan
Multiple Step B and multiple Step A	Line Item	Line Item	Line Item

For example, to make each per-line-item step depend on one plan-level step, set Step B's scope to Plan and Step A's scope to Line Item. For an order that has three line items, DRO creates one Step B for the whole plan and one Step A for each line item, and all three Step A instances wait for that one Step B to finish.

Bundle scope works the same way at the bundle level. When a step's scope is Bundle, DRO creates one instance of the step for each bundle in the order. To pair a Bundle-scoped step with steps at another scope, apply the same rule: Set the dependency scope to the scope of the step that must finish first.

SEE ALSO
Context Definitions for Dynamic Revenue Orchestrator
Import a Fulfillment Step Definition Group
Cross-Plan Dependencies
