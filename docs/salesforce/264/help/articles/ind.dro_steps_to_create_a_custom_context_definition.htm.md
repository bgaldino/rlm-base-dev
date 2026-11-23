---
article_id: ind.dro_steps_to_create_a_custom_context_definition.htm
title: Create Custom Context Definitions for Order Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_steps_to_create_a_custom_context_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_advanced_setup.htm
fetched_at: 2026-11-23
---

# Create Custom Context Definitions for Order Orchestration

During the fulfillment of orders, Dynamic Revenue Orchestrator (DRO) sometimes uses the permissions associated with context definitions. Add a custom context definition by extending the Sales Transaction Context Definition.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
NOTE If you aren't familiar with Context Service and working with Context Definitions, learn Context Service Basics at Trailhead.

Create a custom context definition by choosing nodes, defining their relationship, and adding attributes. These custom definitions are available on the Custom Definitions tab. Create custom definitions by using the Extend action.

Enable Permission for Context Service Users
Create and manage context definitions easily and efficiently by assigning permission set licenses to your users. Add permissions to specific user personas to complete the work assigned to their role. System admin users have default access to Context Service without requiring any specific permission set licenses.
Create Custom Context Definition and Map Attribute to Field
Extend a standard definition that you want to inherit all the standard components such as nodes, attributes, and mappings. Then customize the extended definition based on your requirements by adding components to it.
Map Custom Context Definition with Sales Transaction
To start using a context definition, you must associate the context definition's newly created attribute with the context field in the sales transaction node.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_steps_to_create_a_custom_context_definition.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
