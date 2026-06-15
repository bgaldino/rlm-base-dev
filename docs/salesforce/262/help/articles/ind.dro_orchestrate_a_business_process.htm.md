---
article_id: ind.dro_orchestrate_a_business_process.htm
title: Dynamic Revenue Orchestrator for Business Processes
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_orchestrate_a_business_process.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
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
