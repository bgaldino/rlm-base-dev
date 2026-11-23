---
article_id: ind.qocal_create_object_state_transitions.htm
title: Create Object State Transitions for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_transitions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
fetched_at: 2026-11-23
---

# Create Object State Transitions for Order Lifecycle Management

Define valid status changes between states to control how an order moves through its lifecycle. For example, create a transition that moves an order from Draft to Activated.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_transitions.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
