---
article_id: ind.dro_hi_tech_order_orchestration_template.htm
title: Design Orchestration with the High Tech Order Orchestration Template
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_hi_tech_order_orchestration_template.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-09-05
---

# Design Orchestration with the High Tech Order Orchestration Template

Use the High Tech Order Orchestration Template as a starting point for orders that combine project work, hardware assembly, software provisioning, billing, and revenue scheduling.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

The preconfigured template provides technical products, fulfillment steps, dependencies, and automations for common high tech order scenarios. To install the template, see Install the High Tech Order Orchestration Template.

The template installs these components, which you can adapt to your products and fulfillment processes.

COMPONENT	DESCRIPTION
Technical products	Billing, Project, Hardware Assembly, Tenant Provisioning, Software Provisioning, and Revenue Schedule
Fulfillment step definition groups	One group for each product. Each group contains the fulfillment steps that support delivery and revenue realization
Fulfillment step definitions	The individual steps in each group, including auto tasks, manual tasks, and assetization steps that perform the fulfillment work
Fulfillment step dependency definitions	The relationships that determine the order in which the fulfillment steps run within and across groups
Fulfillment workspace	The workspace and workspace items that organize the fulfillment steps in the workspace designer
Product fulfillment scenarios	The mappings that connect each technical product to its fulfillment step definition group
Apex classes and flows	Automations for processes such as creating billing schedules, generating invoice documents, and sending invoice emails

Adapt the products, fulfillment steps, and automations to your business processes.

How the Template Runs

To enable decomposition, create rules that map your commercial products to the technical products in the template. When an order is submitted, Dynamic Revenue Orchestrator decomposes its products into the template's technical products. The product fulfillment scenarios select the corresponding step definition groups and create a plan that preserves their dependencies.

Users complete manual tasks and milestones in the fulfillment plan. Automated tasks invoke flows for billing and invoicing. Staged assetization steps create fulfillment assets at the configured point in the plan. After invoice document generation completes, the final billing task sends the invoice document to the customer.
