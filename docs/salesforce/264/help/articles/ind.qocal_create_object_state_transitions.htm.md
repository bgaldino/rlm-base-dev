---
article_id: ind.qocal_create_object_state_transitions.htm
title: Create Object State Transitions for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_transitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
fetched_at: 2026-09-04
---

# Create Object State Transitions for Order Lifecycle Management

Define valid status changes between states to control how an order moves through its lifecycle. For example, create a transition that moves an order from Draft to Activated.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create object state values:	
View on orders and object state definitions
Create on object state transitions

Specify the "from" and "to" states to establish authorized paths for order status changes.

From the App Launcher, find and select Object State Definitions.
Click the object state definition that requires transitions.
Click Related.
In the Object State Transitions section, click New.
Enter a name for the transition.
Select the "from" and "to" states for the transition.
Save your changes.
Repeat this step for each status transition that you want to add.
