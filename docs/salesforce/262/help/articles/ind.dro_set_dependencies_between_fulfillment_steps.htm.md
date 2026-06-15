---
article_id: ind.dro_set_dependencies_between_fulfillment_steps.htm
title: Set Dependencies Between Fulfillment Steps
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_set_dependencies_between_fulfillment_steps.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
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

The Fulfillment Workspace arranges the step definitions in the order that they’re completed when an order is submitted.

To create a dependency between steps, follow these instructions:

From the App Launcher, find and select Fulfillment Workspaces.
On the step definition that must finish first, click .
On the step definition that must finish last, click .
Enter the name of the dependency definition, set the dependency scope, and save your changes.
NOTE Cross Plan Scope Considerations:
For the Cross Plan scope, one instance of the step appears per plan when a step in one plan is dependent on a step that’s in another plan.
To use the Cross Plan scope, make sure to configure the Cross Plan context definition in Sales Transaction Context Definition. Then add or import the fulfillment step groups within the Fulfillment Workspace. See Create Custom Context Definitions for Order Orchestration.
NOTE Propogate State to Dependent Step Considerations:
Use the Propagate State to Dependent Step option only if you have created a dependency between a call out or auto task step and a pause step.
After defining the dependency and propagating the state to the dependent step, you can't change the step type value, unless you first set the Propagate State to Dependent Step value to None.
NOTE In-flight Change Considerations:
When a step is amended or canceled because of an in-flight change in the plan, configure whether the step state must propagate to the following step, by using the Propagate State to Dependent Step field. The options are - None, Amended, Canceled, and Both.
When a step is canceled because of an in-flight change in the plan, to reverse the order of step group execution, select the Execute Cancel Step Groups In Reverse Order checkbox.
SEE ALSO
Context Definitions for Dynamic Revenue Orchestrator
Import a Fulfillment Step Definition Group
Cross-Plan Dependencies
