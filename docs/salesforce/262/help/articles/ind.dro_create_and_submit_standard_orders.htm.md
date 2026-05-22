---
article_id: ind.dro_create_and_submit_standard_orders.htm
title: Create and Submit an Order
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_create_and_submit_standard_orders.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Create and Submit an Order

Sales reps submit simple or bundled product orders in Dynamic Revenue Orchestrator (DRO) for decomposition and to instantiate the orchestration plan.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create and submit a Standard Order:	

Fulfillment Designer

OR

DRO Admin

NOTE

Before creating order for fulfillment:

Design Your Order Orchestration solution.
Automate Order Submission to Dynamic Revenue Orchestrator.

To create an order and submit it to DRO:

From the App Launcher, find and select Dynamic Revenue Orchestrator.
From the app navigation menu, select Orders.
Click New Order.
Select an account name for the new order.
Enter an Order Start Date.
Save your work.
On the Order page, click Add Products.
From the Choose Price Book page, select Standard Price Book and save.
From the Add Products page, search for and select the products that you want to add to the order and click Next.
Enter the product quantity and save your changes.
Update the Order status to Activated and submit the order.
To make the Submit Sales Transaction invocable action button available on the Order page, you must create a flow for submitting an order and then add that flow to the Order page. For more information, see Automate Order Submission to Dynamic Revenue Orchestrator.
NOTE Some companies use additional Agentforce Revenue Management features such as Product Catalog Management, Pricing, and Transaction Management. If this is the case, refer to Manage Quote and Order Lifecycle Actions.
SEE ALSO
Developer Documentation: Submit Sales Transactions (API)
