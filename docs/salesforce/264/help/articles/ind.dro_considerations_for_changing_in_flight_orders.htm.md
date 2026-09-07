---
article_id: ind.dro_considerations_for_changing_in_flight_orders.htm
title: Considerations for Changing In-Flight Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_considerations_for_changing_in_flight_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_in_flight_order_changes.htm
fetched_at: 2026-09-05
---

# Considerations for Changing In-Flight Orders

When you set up Dynamic Revenue Orchestrator (DRO) for in-flight order changes, it's important to understand exactly how DRO handles those changes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management where Dynamic Revenue Orchestrator is enabled
Amend and Cancel In-Flight Orders

Amend and Cancel are the types of changes that can be made to an in-flight order. A fulfillment designer can configure how a fulfillment step is compensated or rolled back when the step is amended or canceled because of an in-flight change to the order. These compensations and cancellations are defined by the Amend Step Group and Cancel Step Group, respectively, in the fulfillment step definition.

NOTE You can't amend or cancel an in-flight order through an autotask or callout if the step is part of the same fulfillment plan as the submitted order.
Compensation and Rollback Steps

When an in-flight change amends or cancels a fulfillment order, DRO activates the compensatory or rollback step group linked to the step that the plan has reached. The steps in each group compensate for the amended or canceled steps in the initial plan.

Amend Step Group
A group of steps added to compensate for the step that gets amended because of an in-flight change.
Cancel Step Group
A group of steps added to roll back the step that gets canceled because of an in-flight change. Reverse the order of step group execution by enabling the Execute Cancel Step Groups In Reverse Order option on the Fulfillment Step Dependency Definition page.

DRO inserts the Amend and Cancel step groups into the fulfillment plan between two steps. The groups go after a step in a terminal state, such as Completed or Amended, and before the next step in the Pending state.

To change an order that's already processing an in-flight change, define either the Amend Step Group or the Cancel Step Group to handle later changes.

Supplemental Order Behavior for Amend and Cancel Steps

A supplemental order carries the in-flight changes to an order. Based on the source line item changes, a supplemental action amends or cancels the affected fulfillment steps in the original order's fulfillment plan.

Each fulfillment step has two configurations: an Amend Step Group for in-flight amendment and a Cancel Step Group for in-flight cancellation. When a supplemental action amends or cancels a step, DRO inserts the corresponding step group as compensatory steps. DRO doesn't execute a discarded step or insert a step group for it. The step stays in the plan with an updated status.

IMPORTANT Amending or canceling a completed step doesn't automatically retrigger or recreate it in the fulfillment plan. DRO adds compensatory steps only when you explicitly configure an Amend Step Group or Cancel Step Group. If the step has no Amend Step Group or Cancel Step Group, the completed step remains unchanged.
NOTE A supplemental action updates the step status with the changes captured for the related order line items and fulfillment order line items. It doesn't rerun the orchestration steps. To learn how step statuses change for each supplemental action, see the Step Status Changes from Supplemental Actions table in Point of No Return State Propagation.
WARNING Configuring a large number of Amend and Cancel Step Groups can cause a fulfillment plan to reach the fulfillment platform's limit of 1,000 step groups. Both Amend and Cancel Step Groups count toward this limit. Define each group around only the steps that the change affects.
Point of No Return

Define fulfillment steps as a Point of No Return (PONR). When an item in a product bundle reaches the PONR step, the items in the bundle can no longer be modified. However, items within the same order but outside the bundle remain eligible for amendment or cancellation.

Point of No Return Override

If a step reaches PONR and you want to make some changes to the order line, DRO allows you to override the PONR setting. Achieve this override by passing parameters to the Submit Sales Transaction invocable action, specifically by enabling the allowOverrideOfPointOfNoReturn parameter.

See Developer Documentation: Submit Sales Transaction.

Fulfillment Plan States: Freezing and Frozen

Fulfillment plans in DRO progress through various states that control order fulfillment. The Freezing and Frozen states are significant for applying in-flight order changes.

Freezing
The plan is paused but one or more steps in the plan are in progress. You can't submit in-flight change requests when the plan is in the Freezing state.
Frozen
All steps in the plan are completed or in the Pending state. To amend or cancel an in-flight order, the fulfillment plan must be in this state.
Forcefully Freeze Plan During Execution

To change an in-flight order, the order must be in the Frozen state. But an order containing in-progress steps can't be frozen until the order steps are completed. A fulfillment designer can configure DRO to call the Freeze Sales Transaction invocable action, which forcefully completes the steps and changes the plan status to Frozen.

Configure the Force Plan Freeze During Execution option to determine whether the plan can be forcefully changed to the Frozen state. If you use this option, you must specify how to complete the step before resuming the plan.

SEE ALSO
Configure Inflight Plan Settings for a Fulfillment Step
In-Flight Order Change Example
