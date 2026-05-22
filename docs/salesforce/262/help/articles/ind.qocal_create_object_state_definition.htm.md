---
article_id: ind.qocal_create_object_state_definition.htm
title: Implement an Object State Definition for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Implement an Object State Definition for Order Lifecycle Management

Establish the foundation for managing an order through its lifecycle by defining object state values and valid transitions. Object state definitions help you to control the progression of orders and establish a clear fulfillment process within Agentforce Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create object state definitions for orders:	
View on orders
Create on object state definitions

Configure the state model for orders by selecting the reference object and specifying the application context.

From the App Launcher, find and select Object State Definition.
Enter a name for the definition, for example, Order Lifecycle Management.
Select Order for the reference object.
Select Status for the Reference Field.
Enter RevenueLifecycleManagement for the Application Usage Type.
Enter information for Additional Field and Additional Field Value to apply this definition only to a subset of Agentforce Revenue Management order records.
For example, create two object state definitions to use different lifecycles for B2B and B2C orders.
For the B2B definition, set Additional Field to Channel__c and Additional Field Value to B2B.
For the B2C definition, set Additional Field to Channel__c and Additional Field Value to B2C.
Save your changes.
