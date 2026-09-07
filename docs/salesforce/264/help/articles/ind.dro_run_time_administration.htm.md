---
article_id: ind.dro_run_time_administration.htm
title: Submit Orders for Decomposition and Order Fulfillment
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_run_time_administration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator.htm
fetched_at: 2026-09-05
---

# Submit Orders for Decomposition and Order Fulfillment

Sales reps submit orders to Dynamic Revenue Orchestrator (DRO) for decomposition and fulfillment. During run time, fulfillment operators can track the decomposition and orchestration plans for submitted orders.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
Create and Submit an Order
Sales reps submit simple or bundled product orders in Dynamic Revenue Orchestrator (DRO) for decomposition and to instantiate the orchestration plan.
Monitor Decomposition During Fulfillment
After a user submits an order to Dynamic Revenue Orchestrator (DRO), you can see how products decompose and can spot issues right away.
Order Fulfillment With Time-Awareness
Manage complex, multi-year subscription lifecycles by using time-awareness in fulfillment assets. Instead of using a static snapshot of an asset, time-awareness aligns orchestration with the effective dates of each change, so that additions, cancellations, and renewals of backdated and future-dated orders update only the assets that change in that period.
Monitor Fulfillment During Order Orchestration
Act on steps or learn more about how the fulfillment process is progressing directly from the orchestration plan.
Fulfillment Step States
As steps progress through the fulfillment process, you can check the fulfillment plan to see the state that the steps are in.
View Fulfillment Step History
Monitor the changes to a fulfillment step, such as status modifications, on its detail page by using the Fulfillment Step History related list.
Retry or Complete Multiple Failed Fulfillment Steps
From a list view or queue, retry or complete multiple steps at once. If you complete a step in this way, the step ignores any errors that can otherwise stop the completion of the step.
Handle Conflicts During Asset Date Amendments by Using Submit Order with Validation Flow
It's common to request adjustments to license subscription start dates, either moving them earlier if your users are ready to use them or delaying them if they are not. However, if the order that created the asset has incomplete steps in its fulfillment plan, submitting an asset amendment can result in two orders updating the asset simultaneously. Identify and handle incomplete steps in the fulfillment plan by using the Submit Order with Validation flow.
Configure Custom Logic between Decomposition and Orchestration
To insert custom logic into the fulfillment process between the decomposition and orchestration steps, invoke the two processes separately. The standard Submit Sales Transaction invocable action runs decomposition and orchestration processes sequentially. To decouple the processes, use the individual Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions. Add your custom logic and compose the fulfillment plan with the necessary, up-to-date information. Custom logic is critical if certain data needed for specific validations or data enrichment is only available after decomposition. After the custom logic executes, trigger the Orchestrate Sales Transaction invocable action through various methods, such as custom platform events, Apex triggers, or direct flow actions.
