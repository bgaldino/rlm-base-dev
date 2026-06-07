---
article_id: ind.qocal_manage_orders_in_revenue_lifecycle_management.htm
title: Manage Orders in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_manage_orders_in_revenue_lifecycle_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Manage Orders in Agentforce Revenue Management

Orders signify a formal agreement between your business and the customer, detailing the products, services, and pricing. Learn how to create and manage orders effectively.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Create an Order
Skip the quotation and approval phases for straightforward transactions by generating an order record directly. This process enables you to manage sales that require immediate fulfillment without preliminary quote documentation.
Add an Order Application Usage Type Automatically in Agentforce Revenue Management
Simplify order creation by using an Apex trigger to populate the Application Usage Type field . This field establishes the application context for the record. For all new orders, it creates an AppUsageAssignments record of type RevenueLifecycleManagement.
Order Lifecycle Management
Define the possible states and transitions for an order by using order lifecycle. For example, define states such as Submitted, Processing, and Fulfilled. Then specify that an order state changes from Submitted to Processing and from Processing to Fulfilled.
Order Submission to Dynamic Revenue Orchestrator
Submit sales transactions to Dynamic Revenue Orchestrator (DRO) for fulfillment by using the Submit Sales Transaction invocable action in flows or Apex classes. Automating this process via record-triggered flows makes sure that all eligible records enter the fulfillment pipeline immediately upon meeting specified criteria. Customizing order page layouts to include Orchestration Plan and Orchestration Submission Status fields provides users with real-time visibility into the fulfillment progress.
Modify Activated Orders Before Fulfillment in Agentforce Revenue Management
Use in-flight amendments or supplemental change orders to modify existing orders after activation but before fulfillment. This feature captures changes in a linked order to establish a unified order view, streamline order modification, and improve accuracy.
