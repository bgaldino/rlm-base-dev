---
article_id: ind.dro_orchestrate_non_sales_transaction_business_processes.htm
title: Orchestrate Non-Sales Transaction Business Processes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_non_sales_transaction_business_processes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Orchestrate Non-Sales Transaction Business Processes

Dynamic Revenue Orchestrator (DRO) orchestrates objects even if they aren't based on sales transactions. For example, you can orchestrate the dunning processes by using DRO to trigger personalized workflows based on customer segments. DRO can orchestrate obligations to track and fulfill post-sale milestones like delivery or service level agreements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
USER PERMISSIONS NEEDED
To orchestrate a non-sales transaction business processes:	

Submit Transaction and Orchestrate User

and

Submit Transactions User

and

Permission sets specific to the object to orchestrate

Let's design a workflow to orchestrate for a non-sales transaction-based business process.

DRO accepts any context definition and isn't restricted to the sales transaction context definition. You can create a context definition or use an existing context definition. Map the attributes in the context definition to fields of the object you want to orchestrate. See Custom Context Definition to Orchestrate a Non-Sales Transaction Business Processes.
Create an Orchestration Plan Context Mapping entry to associate the context definition to the orchestration logic within DRO. See Create Orchestration Plan Context Mapping. The orchestration type in the Orchestration Plan Context Mapping should be the same as the usage type of the orchestration components you use in the fulfillment plan. Use the Generic Orchestration Type that is provided out-of-the-box from DRO to orchestrate non-sales transaction objects.
Create a fulfillment workspace and generate an orchestration plan with fulfillment step definitions groups, fulfillment steps, and fulfillment dependencies. Select the Plan or Item dependency scope when creating fulfillment dependencies. Other scopes are not valid for this orchestration. Create a fulfillment scenario to link the object with the correct orchestration plan. To determine selection of the appropriate scenario during fulfillment, define conditions. See Define Orchestration Plan Components.
The usage type of the orchestration components you use in the fulfillment plan should be the same as the orchestration type selected in the Orchestration Plan Context Mapping entry. Add the Usage Type field to the fulfillment scenario, fulfillment step definition groups, fulfillment step definitions, and fulfillment dependencies record pages if it isn't already present.
To show the orchestration plan's submission status and fulfillment progress on the object page, configure the orchestration plan summary component.
To initiate orchestration, submit the order to DRO by using the Orchestrate Transaction invocable action. See Dynamic Revenue Orchestrator Standard Invocable Actions .
