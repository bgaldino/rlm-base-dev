---
article_id: ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm
title: Permission Sets in Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_permissions_in_dynamic_revenue_orchestrator.htm
fetched_at: 2026-11-23
---

# Permission Sets in Dynamic Revenue Orchestrator

Permission sets grant users access to specific objects, fields, and features, and are the recommended way to manage permissions. Dynamic Revenue Orchestrator (DRO) provides standard permission sets for setting up DRO, designing fulfillment, managing fulfillment at run time, and submitting transactions. Assign the permission set that matches each user's role.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
How DRO Access Works

To use DRO, users need the Fulfillment User permission set license. After assigning the license, assign the DRO permission sets that include the permissions users need.

NOTE For the Dynamic Revenue Orchestrator Read Only permission set, assign the DRO Read Only permission set license instead of the Fulfillment User license.

A DRO permission set packages the access a role requires:

User permissions enable DRO pages and invocable actions.
Object permissions and field-level security control access to data.
Org-wide defaults and sharing rules control record visibility, which you set up separately.

Each user has a profile that provides baseline capabilities, such as activating orders. These profile-level permissions are distinct and should not be included in a permission set. Instead, use permission sets to extend baseline access without modifying the user's profile. To manage profile permissions, see Create and Configure Standard Profiles.

DRO Standard Permission Sets

Each standard permission set grants a workspace and the supporting access for its role. Choose the narrowest role that supports the user's work.

Each standard set is the complete role. It includes supporting permissions from Revenue Management, Context Service, Flow, and the Salesforce Platform, even when their names don't mention DRO.

PERMISSION SET	ASSIGN IT TO	ACCESS AND CONSIDERATIONS
DRO Admin User	A Salesforce admin who configures DRO settings, turns on features, and manages the fulfillment framework.	Provides broad access to DRO Setup, design and runtime pages, Context Service administration, flows, product catalogs, and DRO invocable actions. Recommended profile: System Administrator.
Fulfillment Designer	A back-office user who designs product fulfillment frameworks, workspaces, decomposition and enrichment rules, steps, dependencies, and scenarios.	Provides design and configuration access, including fulfillment editors and product catalog management. Doesn't include DRO invocable action access.
Fulfillment Manager/Operator	A back-office user who monitors running orders, failed steps, pending tasks, service-level agreement (SLA) status, and jeopardy indicators.	Provides runtime workspace and decomposition viewer access to retry, edit, and complete fulfillment tasks. Grants Create, Read, Edit, and Delete (CRUD) permissions on Fulfillment Steps and read-only access to other DRO objects. Excludes design-time access and DRO invocable actions.
Submit Transactions User	A user or integration identity that submits transaction requests but doesn't design, monitor, or complete fulfillment.	Grants access to the Submit Order and Submit Sales Transaction invocable actions. Doesn't include DRO design, monitoring, or fulfillment-task access. To submit an order that DRO decomposes and fulfills, also assign Submit Transactions and Fulfillment User.
Submit Transactions and Fulfillment User	A user who submits a sales order that DRO decomposes and fulfills.	Grants access to order transaction submission, product decomposition and enrichment, runtime workspace, fulfillment controls, and invocable actions.
Submit Transactions and Orchestrate User	A user who orchestrates a quote, custom object, or other non-sales transaction.	Grants orchestration engine access for non-sales transactions such as quotes or custom objects.
Dynamic Revenue Orchestrator Read Only	A Salesforce or integration user who views fulfillment progress and doesn't submit, design, or complete fulfillment	Grants read access to the Orchestration Plan Viewer, Decomposition Viewer, Decomposition Workspace, and Dynamic Revenue Orchestrator runtime objects and fields. Doesn't include Create, Edit, Delete, View All Records, or transactional permissions such as Submit Transactions. Requires the DRO Read Only permission set license instead of the Fulfillment User permission set license. To open Decomposition Viewer and Decomposition Workspace, also assign the Product Catalog Management Viewer permission set.
DRO User Permissions

DRO user permissions are the functional capabilities included in the standard DRO permission sets. They enable specific DRO pages, controls, and invocable actions. When you create custom access, add the applicable DRO user permission. then provide its required supporting permissions, object permissions, and field-level security.

USER PERMISSION (LABEL)	DESCRIPTION	INCLUDED IN PERMISSION SET
Administer Dynamic Revenue Orchestrator	Configure DRO and access all DRO pages and actions	DRO Admin User
Design Fulfillment and Orchestration in Dynamic Revenue Orchestrator	Design fulfillment rules, steps, and scenarios in DRO	Fulfillment Designer
Run and Monitor Fulfillment in Dynamic Revenue Orchestrator	Manage and monitor fulfillment, and resolve failed or pending fulfillment steps in DRO	Fulfillment Manager/Operator
Submit and Fulfill Sales Transactions in Dynamic Revenue Orchestrator	Submit orders and sales transactions, trigger fulfillment, and complete fulfillment steps in DRO	Submit Transactions and Fulfillment User
Submit and Orchestrate Non-Sales Transactions in Dynamic Revenue Orchestrator	Submit non-sales transactions and orchestrate their business processes in DRO	Submit Transactions and Orchestrate User
Submit Transactions in Dynamic Revenue Orchestrator	Run the Submit Order and Submit Sales Transaction actions in DRO. Combine the user permission with Submit and Fulfill Sales Transactions or Submit and Orchestrate Non-Sales Transactions to complete the transaction.	Submit Transactions User, Submit Transactions and Fulfillment User, and Submit Transactions and Orchestrate User
Fulfillment User and Run As User

At runtime, DRO executes steps using the configured fulfillment user's permissions, unless a step specifies an alternative in its Run As User field. To configure a fulfillment user, see Fulfillment User and Create Fulfillment Users for Order Orchestration.

The fulfillment user must have at least the DRO Admin User or Submit Transactions and Fulfillment User permissions. For automatic assetization, both the submitting user and the fulfillment user require the Assetize Order permission from Revenue Lifecycle Management.
If a step doesn't specify a Run As User, DRO falls back to the fulfillment plan's execution user, then to the org's Automated Process user.
Specify a Run As User on individual steps that require unique privileges, such as making external system callouts.
SEE ALSO
Knowledge Article: Dynamic Revenue Orchestrator Permissions
View and Manage Users
Create or Clone Profiles
View and Manage Your Permission Set Licenses
Provide Dynamic Revenue Orchestrator Access

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_permission_sets_in_dynamic_revenue_orchestrator.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
