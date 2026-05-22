---
article_id: ind.dro_order_submission_to_dro.htm
title: Automate Order Submission to Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_order_submission_to_dro.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Automate Order Submission to Dynamic Revenue Orchestrator

Create a record-triggered flow that automatically submits Agentforce Revenue Management orders to Dynamic Revenue Orchestrator when the orders are activated.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management

To set up the flow and filter for Agentforce Revenue Management records, see Automate Asset Creation from Orders. After you configure the flow and its decision paths, add the submission action.

In the Agentforce Revenue Management Record branch, click .
Find and select Action.
In the New Action dialog box, specify these details.
Select Submit Order as the action.
For Label, enter Submit Order Action.
For API Name, enter Submit_Order_Action.
Select Prior Values of Triggering Order > Order ID as the order ID.
Click Done.
Save your work.
Enter a label and API name for the flow, and then save your changes.
Activate the flow.
Add an Action to Submit Orders to Dynamic Revenue Orchestrator

To identify and handle incomplete steps in the fulfillment plan before amending the asset, use the Submit Order with Validation flow. See Handle Conflicts During Asset Date Amendments by Using Submit Order with Validation Flow.

To call the decomposition and orchestration processes individually, use the Decompose Sales Transaction and Orchestrate Sales Transaction invocable actions. See Dynamic Revenue Orchestrator Standard Invocable Actions.

To add the Fulfillment Plan and Orchestration Submission Status fields, edit order page layouts. See Customize Page Layouts with the Enhanced Page Layout Editor.

This completes the basic setup for Dynamic Revenue Orchestrator.

To enable other features, see Dynamic Revenue Orchestrator Advanced Setup.

To proceed with the rest of the Agentforce Revenue Management setup, see Set Up Agentforce Revenue Management.
