---
article_id: ind.dro_add_a_fulfillment_user.htm
title: Create Fulfillment Users for Order Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_add_a_fulfillment_user.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_permissions_in_dynamic_revenue_orchestrator.htm
fetched_at: 2026-11-23
---

# Create Fulfillment Users for Order Orchestration

During fulfillment, Dynamic Revenue Orchestrator (DRO) uses the permissions associated with the fulfillment user rather than those of the user who submits an order. You can specify a different user for certain orchestration tasks, but generally, the permissions default to the fulfillment user. Select the fulfillment user from the Dynamic Revenue Orchestrator Settings pane.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To add a fulfillment user:	DRO Admin
The fulfillment user must have at least the DRO Admin User or Submit Transactions and Fulfillment User permissions. For automatic assetization, both the submitting user and the fulfillment user require the Assetize Order permission from Revenue Lifecycle Management.
If a step doesn't specify a Run As User, DRO falls back to the fulfillment plan's execution user, then to the org's Automated Process user.
Specify a Run As User on individual steps that require unique privileges, such as making external system callouts.
From Setup, in the Quick Find box, enter Dynamic Revenue Orchestrator Settings and select it.
Choose one of these options:
User who submitted the order: The permissions and name of the user who submitted the order are used for fulfillment processes.
Other User: Search for and select a user whose permissions and name are used for fulfillment processes.

The fulfillment user is set. You don't need to save your work.

SEE ALSO
Fulfillment User
Permission Sets in Dynamic Revenue Orchestrator
Provide Dynamic Revenue Orchestrator Access

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_add_a_fulfillment_user.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
