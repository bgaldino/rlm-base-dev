---
article_id: ind.dro_define_a_fulfillment_step.htm
title: Define a Fulfillment Step
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_define_a_fulfillment_step.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_define_orchestration_components.htm
fetched_at: 2026-09-05
---

# Define a Fulfillment Step

After you create a fulfillment step definition group in the workspace, add a fulfillment step definition to it. When an order is submitted, Dynamic Revenue Orchestrator (DRO) creates a fulfillment step in the Orchestration Plan for the order based on this definition.

Here's how to create a fulfillment step definition:

From the App Launcher, find and select Fulfillment Workspaces.
Choose a fulfillment step definition group and click Add Step.
Enter a Fulfillment Step Definition Name.
Select a Step Type.
Some step types require additional information. For details on how to configure each step type, see Fulfillment Step Types.
Select a Scope.
The scope determines how many instances of the fulfillment step is created once the orchestration plan is underway. The scope options are:
Plan: One instance of the step appears in the entire orchestration plan.
Bundle: One instance of the step appears per bundle in the order.
Line Item: One instance of the step appears per line item.
Custom: One instance of the step appears per scope identifier. To create a custom fulfillment scope, see Create Custom Fulfillment Scope Configuration.
Optional: Enter a Custom Config Parameter.
A Custom Config Parameter is a step-specific configuration value passed from an autotask step to a Salesforce Flow. Use it to drive custom logic in the flow based on the parameter's value.
Optional: Select a Run As User.
When DRO executes this step, it uses the selected user's permissions. If you don't select a Run As User, then the step is executed as the Fulfillment User as defined in the DRO settings.
Optional: Select an Execution Schedule. For more information, see Configure Steps for Future Execution.
Optional: If you have In-flight amendment enabled in DRO settings, configure In-Flight Order Changes.
Optional: To configure the conditions for running the step, see Define Conditions for a Fulfillment Step to Run.
