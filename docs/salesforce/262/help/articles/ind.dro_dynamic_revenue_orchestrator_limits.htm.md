---
article_id: ind.dro_dynamic_revenue_orchestrator_limits.htm
title: Dynamic Revenue Orchestrator Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_dynamic_revenue_orchestrator_limits.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Dynamic Revenue Orchestrator Limits

Order fulfillment processes are governed by limits on order submission, order line items, fulfillment order line items, and workspace usage. These limits differ for asynchronous and synchronous intake, and Dynamic Revenue Orchestrator responds in specific ways when the limits are exceeded.

REQUIRED EDITIONS
Available in: Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
Order Submission Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	SYNCHRONOUS SUBMISSION LIMIT	ASYNCHRONOUS SUBMISSION LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Fulfillment Orders	The number of high-priority fulfillment orders that can be submitted per hour.	2400	2400	Processes additional orders by using the default priority level or rejects them as configured. See Order Prioritization
Order Line Item Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	SYNCHRONOUS SUBMISSION LIMIT	ASYNCHRONOUS SUBMISSION LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Order Items	The number of order items that can be submitted per order.	200	1000	Rejects order submissions containing additional order items.
Attributes per order line item	The number of attributes that can be processed per line item.	50	100	Rejects order submissions containing additional attributes per order item.
Decomposition Rules	The number of decomposition rules that can be processed per order.	400	2000	Rejects order submissions containing additional decomposition rules.
Enrichment Rule Mapping	The number of enrichment rules that can be defined for a decomposition rule.	20	20	Prevents the creation of records.
Fulfillment Scenarios	The number of fulfillment scenarios that can be defined per order.	400	2000	Rejects order submissions containing additional fulfillment scenarios.
Fulfillment Order Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	SYNCHRONOUS SUBMISSION LIMIT	ASYNCHRONOUS SUBMISSION LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Attributes	The number of attributes that can be processed per order.	3000	3000	Rejects order submissions containing additional attributes.
Fulfillment Order Line Item Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	SYNCHRONOUS SUBMISSION LIMIT	ASYNCHRONOUS SUBMISSION LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Attributes	The number of attributes that can be processed per fulfillment order line item.	50	100	Rejects order submissions containing additional attributes.
Fulfillment Steps	The number of fulfillment steps that can be added to a fulfillment plan.	200	2000	Rejects order submissions containing additional fulfillment steps.
Step Sources	The number of order item sources or fulfillment transaction item sources that can be defined per fulfillment step.	25	125	Rejects order submissions containing additional sources.
Fulfillment Task Assignment Rules	The number of fulfillment task assignment rules that can automatically assign manual tasks to users.	200	200	Prevents additional manual task assignments.
The number of fulfillment task assignment rules that can automatically assign manual tasks to users for a matching source in the step definition.	10	10	Prevents additional manual task assignments.
Non-Sales Transaction Object Orchestration Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	SYNCHRONOUS SUBMISSION LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Fulfillment Scenarios	The number of fulfillment scenarios that can be defined per object.	100	Rejects submissions of objects containing additional fulfillment scenarios.
Fulfillment Steps	The number of fulfillment steps that can be added to a fulfillment plan.	100	Rejects object submissions containing additional fulfillment steps.
Step Sources	The number of sources that can be defined per fulfillment step.	10	Rejects object submissions containing additional sources.
Decomposition Workspace and Fulfillment Workspace Limits
ORCHESTRATION ITEM	LIMIT DESCRIPTION	LIMIT	SYSTEM ACTION IF THE LIMIT IS CROSSED
Decomposition Workspace	The number of products that can be shown in the workspace for a product bundle.	200	Products are filtered based on priority and last modified date. Additional products aren't shown in the workspace.
The number of decomposition rules that can be shown in the workspace.	200	Decomposition rules are filtered based on priority and last modified date. Additional rules aren't shown in the workspace.
The number of decomposition rules related to a product that can be shown on the workspace side panel.	From the product -100 To the product - 100	Decomposition rules are filtered based on priority and last modified date. Additional rules aren't shown in the side panel.
Fulfillment Workspace	The number of fulfillment step groups that can be associated with a fulfillment workspace.	100	The additional step groups that are created aren’t shown in the fulfillment workspace.
The number of dependencies that can be created within a fulfillment step definition group.	100	The additional dependencies that are created aren’t shown in the fulfillment workspace.
The number of fulfillment steps that can be created within a workspace item or fulfillment step definition group.	100	The additional fulfillment steps that are created aren’t shown in the fulfillment workspace.
Expression Set Limits

This section lists the specific limits that apply to expression sets defined using the Decomposition Enrichment Mapping usage type. For additional default limits on expression sets from Business Rules Engine, see Business Rules Engine Default Limits.

LIMIT DESCRIPTION	LIMIT
The number of expression sets.	20
The number of steps in an expression set.	20
The total number of input and output variables in an expression set.	50
