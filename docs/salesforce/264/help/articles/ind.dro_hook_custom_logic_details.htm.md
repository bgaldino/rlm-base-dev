---
article_id: ind.dro_hook_custom_logic_details.htm
title: Configure Custom Logic between Decomposition and Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_hook_custom_logic_details.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_run_time_administration.htm
fetched_at: 2026-09-05
---

# Configure Custom Logic between Decomposition and Orchestration

To insert custom logic into the fulfillment process between the decomposition and orchestration steps, invoke the two processes separately. The standard Submit Sales Transaction invocable action runs decomposition and orchestration processes sequentially. To decouple the processes, use the individual Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions. Add your custom logic and compose the fulfillment plan with the necessary, up-to-date information. Custom logic is critical if certain data needed for specific validations or data enrichment is only available after decomposition. After the custom logic executes, trigger the Orchestrate Sales Transaction invocable action through various methods, such as custom platform events, Apex triggers, or direct flow actions.

The configuration of the flow differs depending on whether you are processing transactions synchronously or asynchronously.

NOTE Provide the same input parameter values in both the Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions. For example, if allowOverrideOfPointOfNoReturn is set to true in the Decompose Sales Transaction invocable action, it must set to true for the Orchestrate Sales Transaction invocable action too.
NOTE The rollback behaviour when an error occurs depends on whether the flow runs synchronously or asynchronously.
Synchronous Rollback: An error causes both decomposition and orchestration artifacts to roll back.
Asynchronous Rollback: Successful decomposition artifacts aren't rolled back if orchestration fails, unless the error happens while composing the fulfillment plan.
Configure Custom Logic in a Synchronous Flow
When you configure the Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions in a synchronous request, the flow executes the actions sequentially.
Configure Custom Logic in an Asynchronous Flow
When you configure the Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions in an asynchronous request, the decomposition process runs in the background. Pause the flow until decomposition is finished before executing the custom logic and the Orchestrate Sales Transaction invocable action.
