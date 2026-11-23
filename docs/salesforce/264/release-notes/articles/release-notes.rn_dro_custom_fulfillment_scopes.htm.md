---
article_id: release-notes.rn_dro_custom_fulfillment_scopes.htm
title: Align Fulfillment Dependencies by Using Custom Scopes
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_dro_custom_fulfillment_scopes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_dynamic_revenue_orchestrator.htm
fetched_at: 2026-11-23
---

# Align Fulfillment Dependencies by Using Custom Scopes

Group and sequence fulfillment steps according to your business criteria by using custom scopes for fulfillment step dependencies. A custom scope, such as a group or ramp segment, aligns plan composition with your fulfillment model, making sure that steps are grouped correctly in complex or ramped orders.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Cloud, with the Revenue Cloud Advanced license.

How:

Set up a Custom Fulfillment Scope Config with an item context tag, an optional asset context tag, and a fallback scope. Then, in a fulfillment step dependency, set the scope to Custom and select the scope. When an order is submitted, Dynamic Revenue Orchestrator builds the plan dependencies based on your scope settings.

SEE ALSO
Salesforce Help: Apply Custom Scopes to Fulfillment Steps and Dependencies (can be outdated or unavailable during release preview)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=release-notes.rn_dro_custom_fulfillment_scopes.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
