---
article_id: ind.qocal_create_object_state_values.htm
title: Create Object State Values for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_values.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Create Object State Values for Order Lifecycle Management

Define the possible states for the order object to establish the stages of your order lifecycle. Ensure the name of your object state values exactly match the API names of your order status picklist values to maintain data integrity.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To create object state values:	
View on orders and object state definitions
Create on object state values

By default, the status field of the order object includes two picklist values: Draft and Activated. Before you create other object state values, create a picklist value for each custom state and sort them in the required sequence. To learn how to use picklists, see Add or Edit Picklist Values.

Add specific status values to your object state definition to represent each stage of the order process.

From the App Launcher, find and select Object State Definitions.
Click the object state definition that you want to add states to.
Click Related.
In the Object State Values section, click New.
Enter the API name of an order status picklist value.
Save your changes.
Repeat this step for each status that you want to add.
NOTE The Reference Record Access Type and Reference Record Layout Field Value fields aren’t applicable for order object state values.
