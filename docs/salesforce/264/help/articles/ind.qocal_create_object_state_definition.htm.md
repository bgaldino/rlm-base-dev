---
article_id: ind.qocal_create_object_state_definition.htm
title: Implement an Object State Definition for Order Lifecycle Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_order_lifecycle_management_using_object_state_definitions.htm
fetched_at: 2026-11-23
---

# Implement an Object State Definition for Order Lifecycle Management

Establish the foundation for managing an order through its lifecycle by defining object state values and valid transitions. Object state definitions help you to control the progression of orders and establish a clear fulfillment process within Revenue Cloud.

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
Enter information for Additional Field and Additional Field Value to apply this definition only to a subset of Revenue Cloud order records.
For example, create two object state definitions to use different lifecycles for B2B and B2C orders.
For the B2B definition, set Additional Field to Channel__c and Additional Field Value to B2B.
For the B2C definition, set Additional Field to Channel__c and Additional Field Value to B2C.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.qocal_create_object_state_definition.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
