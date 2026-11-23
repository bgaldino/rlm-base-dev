---
article_id: ind.dro_orchestrate_a_business_process.htm
title: Dynamic Revenue Orchestrator for Business Processes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_a_business_process.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_advanced_setup.htm
fetched_at: 2026-11-23
---

# Dynamic Revenue Orchestrator for Business Processes

Use Dynamic Revenue Orchestrator (DRO) to design and orchestrate any object regardless of whether is is based on a sales transaction. Review the differences between sales transaction-based and non-sales transaction-based business process orchestration setup.

REQUIRED EDITIONS
Available in: both Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
FEATURE	SALES TRANSACTION BUSINESS PROCESS	NON-SALES TRANSACTION BUSINESS PROCESS
Sample use cases	Quote to Order, Order to Cash, Incidents, Cases, Service Requests	Dunning Process, Obligations Management, Compliance Verification
Primary goal	Streamline the standard sales-to-service lifecycle	Streamline the pre and post-sale workflows
Object origin	Derived from the Product2 object	Independent of Product2 object. For example, Collection Plan or Obligations.
Context definition	Extends Sales Transaction context definition	Defines a custom context definition or extends a standard context definition, such as Billing, with the required mapping.
Orchestration type	Predefined Sales Transaction usage type	Predefined Generic Orchestration Type
NOTE Dynamic Revenue Orchestrator supports multiple rule libraries based on the plan usage type. The system identifies the correct library using specific API naming conventions: DRORuleLibrary for the default fulfillment plan usage type, and DRORuleLibrary[UsageTypeName] for others. If your existing default rule library uses an API name other than DRORuleLibrary, create a new library with the API name DRORuleLibrary and migrate your rules to it. Failure to do so prevents you from creating, editing, or executing rules.
Orchestrate Sales Transaction Business Processes
Set up a workflow to orchestrate business processes such as Quote to Order, Order to Cash, Incidents, Cases, Service Requests, and custom objects. First, extend the Sales Transaction context definition. Then, clone and save the required mapping, update the mapping to link the Sales Transaction node attributes to your business object's fields, create a procedure plan definition and associate it with the new context definition, and then configure the new context definition for the Sales Transaction Context Definition. Finally, submit the business process for orchestration.
Orchestrate Non-Sales Transaction Business Processes
Dynamic Revenue Orchestrator (DRO) orchestrates objects even if they aren't based on sales transactions. For example, you can orchestrate the dunning processes by using DRO to trigger personalized workflows based on customer segments. DRO can orchestrate obligations to track and fulfill post-sale milestones like delivery or service level agreements.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_a_business_process.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
