---
article_id: ind.dro_cross_plan_dependencies.htm
title: Cross-Plan Dependencies
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_cross_plan_dependencies.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Cross-Plan Dependencies

Cross-plan dependencies establish connections between steps in different fulfillment plans that are part of related orders. Use cross-plan dependencies when a step in one order's fulfillment plan relies on the completion of a step in a different order's fulfillment plan.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

For example, consider a scenario where the fulfillment plan for Product A contains a platform service activation step. The platform is provisioned as a part of the fulfillment plan for Product B. The two products are part of independent order fulfillment plans belonging to separate orders. Use cross-plan dependencies to make sure that the platform service activation step starts only after the platform provisioning step is complete.

Fulfillment Plan Design

Prerequisites:

Provide a unique Orchestration Group Key for Dynamic Revenue Orchestrator (DRO) to group related orders. The Orchestration Group Key points to an attribute defined under the Sales Transaction node.
To establish ‌fulfillment plans that are grouped based on Orchestration Group Key, map context definitions to the Orchestration Group Key attribute. See Create Custom Context Definitions for Order Orchestration.

To design the fulfillment plan:

In the Fulfillment Workspace, select Cross Plan scope while defining the dependency. See Set Dependencies Between Fulfillment Steps.
Organize fulfillment steps so that dependent steps in one plan wait for the steps they rely on in another plan to complete.
Avoid bidirectional dependencies, where one plan is dependent on a second plan that, in turn, depends on the first. If you set up bidirectional dependencies, DRO doesn’t generate dependencies.
Orchestration

During the fulfillment process:

Access dependencies from the real-time plan view and open the related plans or steps to take action.
Review steps that have cross-plan dependencies within the fulfillment plan. See Monitor Decomposition During Fulfillment.
Submit orders in a specific sequence, so that orders with dependent steps are submitted later. For example, to activate a service before billing the customer, first submit the order with the Activate Service step, and then submit the order with the Bill Customer step.
Take actions such as marking a step as complete and accessing plan and step dependencies from the External Dependencies tab. See Orchestration Plan Actions and Information.
SEE ALSO
Import a Fulfillment Step Definition Group
Set Dependencies Between Fulfillment Steps
