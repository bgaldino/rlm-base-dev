---
article_id: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
title: Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_order_lifecycle_management_using_object_state_definitions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Order Lifecycle Management

Define the possible states and transitions for an order by using order lifecycle. For example, define states such as Submitted, Processing, and Fulfilled. Then specify that an order state changes from Submitted to Processing and from Processing to Fulfilled.

Control access to specific states or state transitions by using custom permissions. Define different lifecycles for different application usage types. For each application usage type, create multiple lifecycles and enter the criteria to specify which lifecycle is applicable. Use object state definitions to define order lifecycles.

Order Lifecycle States and Transitions
Familiarize yourself with the specific states and transitions used to manage an order through its lifecycle. Use this example and the accompanying object state definitions to configure valid status changes and establish clear fulfillment milestones in your Salesforce org.
Implement an Object State Definition for Order Lifecycle Management
Establish the foundation for managing an order through its lifecycle by defining object state values and valid transitions. Object state definitions help you to control the progression of orders and establish a clear fulfillment process within Agentforce Revenue Management.
Create Object State Values for Order Lifecycle Management
Define the possible states for the order object to establish the stages of your order lifecycle. Ensure the name of your object state values exactly match the API names of your order status picklist values to maintain data integrity.
Create Object State Transitions for Order Lifecycle Management
Define valid status changes between states to control how an order moves through its lifecycle. For example, create a transition that moves an order from Draft to Activated.
Control Access to States and State Transitions
Create custom permissions to restrict or grant access to order states and transitions for specific user groups. Assigning these permissions ensures that only authorized agents move an order to its next supported stage in the fulfillment process.
Activate an Object State Definition
To use an object state definition, you must activate it.
