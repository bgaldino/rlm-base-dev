---
article_id: ind.dro_dynamic_revenue_orchestrator.htm
title: Order Orchestration in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_dynamic_revenue_orchestrator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Order Orchestration in Agentforce Revenue Management

Dynamic Revenue Orchestrator (DRO) breaks down a single commercial order into multiple, manageable fulfillment steps. You can execute a tailored fulfillment plan for each product or service.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
NOTE Learn the fundamentals in Dynamic Revenue Orchestrator Foundations.

Dynamic Revenue Orchestrator breaks down a customer's commercial order into the individual technical products, services, and tasks that are needed to fulfill it. The decomposition process bridges the gap between how a product is sold by sales reps and how it is actually delivered and managed by your order fulfillment team.

After order items are decomposed into fulfillment line items, an orchestration fulfillment plan tracks the stages and tasks required to fulfill the order to completion. A fulfillment plan can contain prioritization rules, SLAs, external callouts, automated tasks, manual tasks, and order fallout contingencies.

You can use DRO to orchestrate Industries Configure, Price, Quote (CPQ) orders. Because DRO is preintegrated with Industries CPQ, you can use DRO without migrating commercial product data out of Enterprise Price Catalog (EPC). See Salesforce Release Note: Integrate DRO with Industries CPQ.

Here's a high-level summary of the steps required to build your DRO solution.

Create your technical product catalog.
Define how products decompose using decomposition rules, field mapping, and execution rules.
Create fulfillment plans using a visual plan editor in the fulfillment workspace.
Define fulfillment steps and product fulfillment scenarios for each of your fulfillment plans.
Define rules for handling SLA jeopardy and order fallout.
Monitor orchestration in real time using the fulfillment orchestration dashboard.

To migrate product fulfillment decomposition rules, fulfillment scenarios, fulfillment step definitions, and fulfillment task assignment rules between Salesforce orgs, use Data API. For high-volume data transfers, use Bulk API to move these records and their associated condition data.
