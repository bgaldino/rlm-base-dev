---
article_id: ind.dro_retry_or_complete_multiple_failed_fulfillment_steps.htm
title: Retry or Complete Multiple Failed Fulfillment Steps
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_retry_or_complete_multiple_failed_fulfillment_steps.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Retry or Complete Multiple Failed Fulfillment Steps

From a list view or queue, retry or complete multiple steps at once. If you complete a step in this way, the step ignores any errors that can otherwise stop the completion of the step.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To view and edit fulfillment:	

Fulfillment Manager/Operator

OR

DRO Admin User

Complete and Retry buttons are available only if the Fallout and SLA Settings setting is turned on.

Sometimes a number of fulfillment steps fail because a system is down. When the system comes back online, the fulfillment designer can bulk retry the steps that failed, or mark the steps complete, rather than addressing them one at a time.

From the App Launcher, find and select Fulfillment Steps.
From the App Launcher, find and select Fulfillment Steps.
Select the list view for the queue that contains the failed steps, or select the Fatally Failed Fulfillment Steps list view.
Select the relevant steps, and then click Retry or Complete.
NOTE You can retry a step if it's in the Failed or Fatally Failed state and the plan is in the In Progress state.

You can complete a step if the plan is in the Freezing state and the step is in the In Progress state, or the plan is in the In Progress state and the step is in either the In Progress, Failed, or Fatally Failed state.

If you select some items that are eligible to be retried or completed, and others that aren't, then only the eligible ones are successful.
