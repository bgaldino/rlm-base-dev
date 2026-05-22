---
article_id: ind.dro_orchestrate_non_sales_transaction_business_processes_context.htm
title: Considerations for Creating a Non-Sales Transaction Context Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_non_sales_transaction_business_processes_context.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Considerations for Creating a Non-Sales Transaction Context Definition

To orchestrate a non-sales transaction business process, create a context definition and map it to the fields of the object to orchestrate. You can also extend an existing context definition by adding a mapping to the object that you want to orchestrate. Keep these considerations in mind when creating a custom context definition and its mapping.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
USER PERMISSIONS NEEDED
To create or extend the context definition:	DRO Admin User

Prerequisite: Enable Permission for Context Service Users.

See Context service.

Define one root node for your object. To orchestrate a collection like a Collection Plan object with multiple items, add child item nodes.
Define an Id attribute for root and child nodes (if applicable). The Id is used to identify the record to orchestrate. Map the Id attribute to the object's Id field.
Define the StartDate attribute used to schedule the fulfillment steps.
To show an identifiable label for the context definition, define a Name attribute . Otherwise, the record Id is shown.
Generate tags for all the attributes.
Add appropriate mappings with the root and child nodes mapped to their respective object fields based on your use case, and activate the context definition.
NOTE
For every attribute tag in a rule condition, define a corresponding object field mapping to prevent execution failures during rule evaluation or fulfillment.
To maintain data consistency across the orchestration lifecycle and to provision multiple mappings, map all the root nodes and applicable child nodes to their respective objects.
