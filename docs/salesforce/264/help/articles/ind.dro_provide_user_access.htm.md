---
article_id: ind.dro_provide_user_access.htm
title: Provide Dynamic Revenue Orchestrator Access
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_provide_user_access.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_permissions_in_dynamic_revenue_orchestrator.htm
fetched_at: 2026-11-23
---

# Provide Dynamic Revenue Orchestrator Access

Assign the appropriate permission set to give users Dynamic Revenue Orchestrator access, and review the permissions included in a permission set.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud
USER PERMISSIONS
NEEDED
To configure deep cloning for fulfillment workspaces:	DRO Admin

Standard DRO permission sets bundle the user, object, and field-level permissions each role needs, so assigning one is usually enough. For cases outside those roles, create a custom permission set. You'll need to configure each access layer yourself: user permissions, object permissions, and field-level security. For the full set of available permissions, see Permission Sets in Dynamic Revenue Orchestrator.

Prepare the user for DRO. Identify the user's responsibilities and required access and assign the Fulfillment User permission set license. For assignment steps, see Manage Permission Set Assignments. See Assign a Permission Set License to a User. Note: The Dynamic Revenue Orchestrator Read Only permission set requires the DRO Read Only permission set license. Do not assign the Fulfillment User permission set license to users who only require read-only access.
Turn on DRO. See Turn On Dynamic Revenue Orchestrator.
Match the user to a permission set. Check whether a standard DRO permission set provides the access the user requires.
If yes, select the set with the least required access and assign it.
If no, start from the closest standard set as a base. Create a custom permission set, add the missing DRO and supporting user permissions, object permissions, and field-level security, and then assign it.
Confirm access works as expected. Verify the user's functional and data access. For order users, confirm Create, Read, Edit, and Delete (CRUD) access to order records. For example, use an expression set to append text to cloned record names or assign a different value to a custom field.
To review the exact user permissions, object access, and field-level security that a specific permission set grants, view its overview page in Setup.
From Setup, enter Permission Sets in the Quick Find box, and select Permission Sets.
Select the permission set that you want to view, such as DRO Admin User.
Click View Summary to see the permission set's enabled object, user, field, and custom permissions, and the permission set groups that include it.
SEE ALSO
Permission Sets in Dynamic Revenue Orchestrator
Create Fulfillment Users for Order Orchestration

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_provide_user_access.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
