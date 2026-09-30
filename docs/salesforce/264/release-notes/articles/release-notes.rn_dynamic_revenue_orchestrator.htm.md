---
article_id: release-notes.rn_dynamic_revenue_orchestrator.htm
title: Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_dynamic_revenue_orchestrator.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Dynamic Revenue Orchestrator

Orchestrate ramp deals. Submit amendments, renewals, and cancellations, and roll them back before they take effect. Keep actions, quantities, and dates accurate by using time-aware assets. Fulfill ramped asset amendments, apply staged assetization to ramped segments, sequence multiyear orchestration steps by time period, and align dependencies among fulfillment steps by using custom fulfillment scopes. Speed up design by cloning fulfillment workspaces, and gain visibility into multiyear orders with the enhanced Decomposition Viewer.

Orchestrate Backdated and Future-Dated Contract Changes Automatically
Fulfill amendments, renewals, and cancellations with past or future effective dates, and roll back future-dated changes in assets before they take effect. During decomposition, Dynamic Revenue Orchestrator evaluates the future state of each fulfillment asset to make sure that fulfillment actions, quantities, and dates reflect the correct time period, even for complex subscriptions and multiyear deals. Time-aware fulfillment assets capture quantities and attributes for each time period to guarantee correct provisioning based on the effective date rather than the submission date.
Streamline Fulfillment of Ramped Asset Amendments
When you add ramp segments or cancel future ones, Dynamic Revenue Orchestrator (DRO) updates the fulfillment order line items and related assets, regardless of your organization's time-aware fulfillment settings.
Eliminate Fulfillment Delays by Using Staged Assetization for Ramped Products
Assetize ramped products during fulfillment plan execution instead of waiting for the plan to complete. Asset creation stays aligned with how you deliver and recognize revenue on multiyear deals. The Staged Assetize step supports both order line item and fulfillment order line item sources of ramped products. Fulfill ramped products with the same flexibility as standard products.
Automate Multiyear Ramp Deal Orchestration with Sequenced Steps
Sequence fulfillment steps chronologically across ramped deals. Dynamic Revenue Orchestrator (DRO) generates plans that respect time segments, so year 1 steps execute before year 2 steps. DRO resolves dependencies across time segments, prevents plan stalls, and enables provisioning of multiyear subscriptions. Sequencing applies to both standard and custom scopes, such as ramp or group identifiers. For finer control over execution timing, configure future-dated steps.
Align Fulfillment Dependencies by Using Custom Scopes
Group and sequence fulfillment steps according to your business criteria by using custom scopes for fulfillment step dependencies. A custom scope, such as a group or ramp segment, aligns plan composition with your fulfillment model, making sure that steps are grouped correctly in complex or ramped orders.
Clone and Reuse Fulfillment Workspaces
Maintain consistent logic, rapidly scale operations, and standardize orchestration across your product catalog by cloning a fulfillment workspace in a single step. Duplicating a workspace copies its step definition groups, step definitions, and dependencies into a new workspace record.
Navigate Orders Easily with the Enhanced Decomposition Viewer
See order decomposition details clearly on the Decomposition Viewer. Line items list their subactions, and decomposition details show attribute names instead of code. When you turn on time-awareness, the time segments for each product are in chronological order while preserving bundle hierarchies, so multiyear orders are easier to validate.
Changed Objects in Dynamic Revenue Orchestrator
Do more with these changed Dynamic Revenue Orchestrator objects.
