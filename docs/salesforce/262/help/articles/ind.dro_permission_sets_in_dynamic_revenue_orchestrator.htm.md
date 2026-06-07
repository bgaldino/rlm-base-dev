---
article_id: ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm
title: Permission Sets in Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Permission Sets in Dynamic Revenue Orchestrator

A permission set is a collection of settings and permissions that give users access to various tools and functions. Permission sets extend the functional access of the users without changing their profiles and are the recommended way to manage user permissions.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
Create Users and Profiles

To begin, create users for Dynamic Revenue Orchestrator (DRO). Then assign users the appropriate permission sets. To help you plan, refer to the list of permission sets in DRO. Users must have create, read, update, and delete permissions for orders.

When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

Permission Sets in Dynamic Revenue Orchestrator
DRO Admin User: Gives access to the DRO app settings and all of its entities. This permission alone doesn't allow a user to submit an order.
Submit Transactions and Fulfillment User: Submit orders to DRO and call the invocable submitOrder action. Typically, users assigned this permission set perform order decomposition, plan composition, and plan execution.
NOTE To ensure that products are automatically assetized at the end of fulfillment, the user that submits the order must have the Assetize Order permission from the Revenue Lifecycle Management permission sets.
Submit Transactions User: Submit transactions to DRO and call the invocable actions. This permission set allows users to submit transaction requests, but doesn’t provide access to any design or fulfillment tasks. See: Fulfillment User
Fulfillment Designer: Gives access to all design time entities and interfaces that you require to configure products, decomposition rules, fulfillment plans, and scenarios.
Submit Transactions and Orchestrate User: Submit transactions to DRO. This permission set doesn’t include product and order permissions. With this permission set along with the Submit Transactions User permission set, users can orchestrate non-sales transactions.
SEE ALSO
View and Manage Users
Create or Clone Profiles
View and Manage Your Permission Set Licenses
