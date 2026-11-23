---
article_id: ind.dro_advanced_setup.htm
title: Dynamic Revenue Orchestrator Advanced Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_advanced_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator.htm
fetched_at: 2026-11-23
---

# Dynamic Revenue Orchestrator Advanced Setup

Dynamic Revenue Orchestrator provides advanced setup options to customize and extend its core functionalities that is crucial for leveraging the product's full power and tailoring it to specific business needs.

Create Queues for Dynamic Revenue Orchestrator
Create Salesforce queues to contain fatally failed steps: For example, you can create a queue for each group in your organization that handles fallout. These queues must include Fulfillment Step as a supported object.
Turn On Future Dated Steps
Turn on Future Dated Steps feature to configure steps to execute at a future date and  time.
Turn On In-Flight Amendments
Enable your order reps to change fulfillment requests that are in progress. By enabling In-Flight Amendments, users can modify the order or specific line items, or even cancel the entire order or parts of it.
Create Custom Context Definitions for Order Orchestration
During the fulfillment of orders, Dynamic Revenue Orchestrator (DRO) sometimes uses the permissions associated with context definitions. Add a custom context definition by extending the Sales Transaction Context Definition.
Dynamic Revenue Orchestrator for Business Processes
Use Dynamic Revenue Orchestrator (DRO) to design and orchestrate any object regardless of whether is is based on a sales transaction. Review the differences between sales transaction-based and non-sales transaction-based business process orchestration setup.
Create Custom Fulfillment Scope Configuration
Custom scopes use a configurable field in the line item or product object as the scope identifier. This identifier defines how fulfillment line items and steps are instantiated. During decomposition and orchestration, custom scopes group fulfillment order line items and steps according to the scope identifier.
Turn On Time-Awareness
Dynamic Revenue Orchestrator (DRO) supports both time-agnostic and time-aware data. During decomposition and assetization, time-awareness evaluates timelines to identify changes in fulfillment asset quantities and attributes over time.
Configure Deep Cloning for Fulfillment Workspaces
Deep cloning uses the preconfigured context definition FulfillmentWorkspaceDeepCloneContext by default. Configure deep clone settings to include supported custom fields or objects, or to transform field values during cloning.
Install the High Tech Order Orchestration Template
Install the preconfigured High Tech Order Orchestration Template from Salesforce Go. Use its products, fulfillment steps, dependencies, and automations as a starting point for common high tech order scenarios.
SEE ALSO
Dynamic Revenue Orchestrator Basic Setup

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_advanced_setup.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
