---
article_id: ind.dro_configure_inflight_plan_settings.htm
title: Configure Inflight Plan Settings for a Fulfillment Step
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_inflight_plan_settings.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Configure Inflight Plan Settings for a Fulfillment Step

As part of creating fulfillment steps, you can configure inflight plan settings to handle customer requests to add, amend, cancel, or otherwise change their order before the order is committed by a sales rep.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To configure inflight plan settings:	

Fulfillment Designer

OR

DRO Admin User

To configure inflight plan settings, first create a fulfillment step using the fulfillment workspace. For more information, see Define Orchestration Plan Components.

Select an Amend Step Group.
Select a Cancel Step Group.
To apply the cancel step groups in reverse order of execution, see Set Dependencies Between Fulfillment Steps.
Configure the Point of No Return behavior. In the Available pane, select the type of source change (Changes Denied) to be applied to the line item, then click  to move the source change to the Chosen field. This selection ensures that when the fulfillment plan reaches this step, no changes to the order items in the bundle are allowed.
Optional: Force Plan Freeze During Execution. Select an option other than the default option to allow order representatives to forcefully freeze the plan. Specify how to complete the step before resuming the plan. Choose an action to apply to the In Progress step:
Never: The plan freezes only after the step is completed. Until then, the plan is in a Freezing state. This is the default option.
Yes But Forcefully Complete the Step: Moves the plan to a Frozen state, forcefully completes the step, and then resumes the plan if the related line item is amended or canceled.
Save your work.
