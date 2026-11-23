---
article_id: ind.dro_orchestrate_non_sales_transaction_business_processes.htm
title: Orchestrate Non-Sales Transaction Business Processes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_non_sales_transaction_business_processes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_orchestrate_a_business_process.htm
fetched_at: 2026-11-23
---

# Orchestrate Non-Sales Transaction Business Processes

Dynamic Revenue Orchestrator (DRO) orchestrates objects even if they aren't based on sales transactions. For example, you can orchestrate the dunning processes by using DRO to trigger personalized workflows based on customer segments. DRO can orchestrate obligations to track and fulfill post-sale milestones like delivery or service level agreements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud
USER PERMISSIONS NEEDED
To orchestrate a non-sales transaction business processes:	

Submit Transaction and Orchestrate User

and

Submit Transactions User

and

Permission sets specific to the object to orchestrate

Let's design a workflow to orchestrate for a non-sales transaction-based business process.

NOTE
The usage type of the orchestration components you use in the fulfillment plan should be the same as the orchestration type selected in the Orchestration Plan Context Mapping entry.
Add the Usage Type field to the fulfillment scenario, fulfillment step definition groups, fulfillment step definitions, and fulfillment dependencies record pages if it isn't already present.
DRO accepts any context definition and isn't restricted to the sales transaction context definition. You can create a context definition or use an existing context definition. Map the attributes in the context definition to fields of the object you want to orchestrate. See Custom Context Definition to Orchestrate a Non-Sales Transaction Business Processes.
Create an Orchestration Plan Context Mapping entry to associate the context definition to the orchestration logic within DRO. See Create Orchestration Plan Context Mapping. Use the Generic Orchestration Type that is provided out-of-the-box from DRO to orchestrate non-sales transaction objects.
Create a fulfillment workspace and generate an orchestration plan with fulfillment step definitions groups, fulfillment steps, and fulfillment dependencies. Select the Plan or Item dependency scope when creating fulfillment dependencies. Other scopes are not valid for this orchestration.
Create a fulfillment scenario to link the object with the correct orchestration plan. To determine selection of the appropriate scenario during fulfillment, define conditions. See Define Orchestration Plan Components.
To show the orchestration plan's submission status and fulfillment progress on the object page, configure the orchestration plan summary component.
To initiate orchestration, submit the order to DRO by using the Orchestrate Transaction invocable action. See Dynamic Revenue Orchestrator Standard Invocable Actions .
Considerations for Creating a Non-Sales Transaction Context Definition
To orchestrate a non-sales transaction business process, create a context definition and map it to the fields of the object to orchestrate. You can also extend an existing context definition by adding a mapping to the object that you want to orchestrate. Keep these considerations in mind when creating a custom context definition and its mapping.
Requirements for Creating Orchestration Plan Context Mapping
Create an orchestration plan context mapping entry to connect the business data in an object to the orchestration logic within Dynamic Revenue Orchestrator (DRO) by using the orchestration type. DRO includes the Generic orchestration type to orchestrate non-sales transaction objects.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_non_sales_transaction_business_processes.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
