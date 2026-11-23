---
article_id: ind.qocal_create_object_state_values.htm
title: Create Object State Values for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_values.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_values.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
